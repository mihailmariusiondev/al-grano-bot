import aiosqlite
from typing import Optional, List, Dict, Tuple
from ..utils.logger import logger
from utils.constants import CLEANUP_THRESHOLDS
from datetime import datetime


class DatabaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            self.db_path: Optional[str] = None
            self.conn: Optional[aiosqlite.Connection] = None
            self.logger = logger.get_logger("db_service")
            self.initialized = True

    async def initialize(self, db_path: str):
        """Initialize database connection and create tables if needed"""
        try:
            self.db_path = db_path
            self.conn = await aiosqlite.connect(db_path)
            self.conn.row_factory = aiosqlite.Row

            # Create tables
            await self.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_user (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            await self.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_config (
                    chat_id INTEGER PRIMARY KEY,
                    max_summary_length INTEGER DEFAULT 2000,
                    language TEXT DEFAULT 'es',
                    auto_summarize BOOLEAN DEFAULT FALSE,
                    auto_summarize_threshold INTEGER DEFAULT 50,
                    cleanup_days INTEGER DEFAULT 30,
                    cleanup_min_messages INTEGER DEFAULT 1000,
                    cleanup_threshold INTEGER DEFAULT 10000,
                    is_bot_started BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            await self.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_message (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    user_id INTEGER,
                    message_text TEXT,
                    telegram_message_id INTEGER,
                    telegram_reply_to_message_id INTEGER,
                    message_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES chat_config(chat_id),
                    FOREIGN KEY (user_id) REFERENCES telegram_user(user_id)
                )
            """
            )

            self.closed = False
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise

    async def execute(
        self, query: str, params: tuple = (), auto_commit: bool = True
    ) -> None:
        """Execute a query (INSERT, UPDATE, DELETE)"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        async with self.conn.cursor() as cursor:
            await cursor.execute(query, params)
            await self.conn.commit()

    async def execute_transaction(self, queries: List[Tuple[str, tuple]]) -> None:
        """Execute multiple queries in a transaction"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        async with self.conn.cursor() as cursor:
            try:
                await cursor.execute("BEGIN TRANSACTION")
                for query, params in queries:
                    await cursor.execute(query, params)
                await self.conn.commit()
            except Exception as e:
                await self.conn.rollback()
                self.logger.error(f"Transaction failed: {e}")
                raise

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch a single row from the database"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        async with self.conn.cursor() as cursor:
            cursor.row_factory = aiosqlite.Row
            await cursor.execute(query, params)
            result = await cursor.fetchone()
            return dict(result) if result else None

    async def close(self):
        """Close the database connection"""
        if self.conn:
            await self.conn.close()
            self.logger.info("Database connection closed")
            self.conn = None

    async def is_premium_user(self, user_id: int) -> bool:
        """Check if a user has premium status"""
        try:
            user = await self.fetch_one(
                "SELECT is_premium FROM telegram_user WHERE user_id = ?", (user_id,)
            )
            return user["is_premium"] if user else False
        except Exception as e:
            self.logger.error(f"Error checking premium status for user {user_id}: {e}")
            return False

    @property
    def closed(self) -> bool:
        """Check if database connection is closed"""
        return self.conn is None or self.conn.closed

    async def get_recent_messages(self, chat_id: int, limit: int = 300):
        """Get recent messages from a chat"""
        try:
            async with self.conn.cursor() as cursor:
                cursor.row_factory = aiosqlite.Row
                await cursor.execute(
                    """
                    SELECT u.first_name, m.message_text, m.telegram_message_id, m.telegram_reply_to_message_id
                    FROM telegram_message m
                    INNER JOIN telegram_user u ON m.user_id = u.user_id
                    WHERE m.chat_id = ?
                    ORDER BY m.id DESC
                    LIMIT ?
                    """,
                    (chat_id, limit),
                )
                rows = await cursor.fetchall()
                return [
                    {
                        "user": {"firstName": row["first_name"]},
                        "message": {
                            "messageText": row["message_text"],
                            "telegramMessageId": row["telegram_message_id"],
                            "telegramReplyToMessageId": row[
                                "telegram_reply_to_message_id"
                            ],
                        },
                    }
                    for row in rows
                ]
        except Exception as e:
            self.logger.error(f"Error fetching recent messages: {e}")
            return []

    async def save_message(
        self,
        chat_id: int,
        user_id: int,
        message_text: str,
        telegram_message_id: int,
        telegram_reply_to_message_id: int,
        message_type: str,
    ):
        """Save a message"""
        try:
            await self.execute(
                """
                INSERT INTO telegram_message (
                    chat_id, user_id, message_text, telegram_message_id,
                    telegram_reply_to_message_id, message_type
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    chat_id,
                    user_id,
                    message_text,
                    telegram_message_id,
                    telegram_reply_to_message_id,
                    message_type,
                ),
            )
            self.logger.info(f"Message saved for chat ID: {chat_id}")
        except Exception as e:
            self.logger.error(f"Error saving message: {e}")

    async def get_or_create_user(
        self, user_id: int, username: str, first_name: str, last_name: str
    ):
        """Get user or create if not exists"""
        try:
            existing_user = await self.fetch_one(
                "SELECT * FROM telegram_user WHERE user_id = ?", (user_id,)
            )

            if existing_user:
                if (
                    existing_user["username"] != username
                    or existing_user["first_name"] != first_name
                    or existing_user["last_name"] != last_name
                ):
                    await self.execute(
                        """
                        UPDATE telegram_user
                        SET username = ?, first_name = ?, last_name = ?
                        WHERE user_id = ?
                        """,
                        (username, first_name, last_name, user_id),
                    )
                    self.logger.info(f"User updated: {user_id}")
            else:
                await self.execute(
                    """
                    INSERT INTO telegram_user (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, username, first_name, last_name),
                )
                self.logger.info(f"User created: {user_id}")

            return await self.get_user(user_id)
        except Exception as e:
            self.logger.error(f"Error getting or creating user: {e}")
            return None

    async def get_user(self, user_id: int):
        """Get user"""
        try:
            return await self.fetch_one(
                "SELECT * FROM telegram_user WHERE user_id = ?", (user_id,)
            )
        except Exception as e:
            self.logger.error(f"Error fetching user: {e}")
            return None

    async def get_chat_config(self, chat_id: int) -> Dict:
        """Get chat configuration, creating default if not exists"""
        try:
            # Try to get existing config
            query = "SELECT * FROM chat_config WHERE chat_id = ?"
            config = await self.fetch_one(query, (chat_id,))
            if not config:
                # Create default config if none exists
                await self.execute(
                    """
                    INSERT INTO chat_config (
                        chat_id,
                        max_summary_length,
                        language,
                        auto_summarize,
                        auto_summarize_threshold,
                        cleanup_days,
                        cleanup_min_messages,
                        cleanup_threshold,
                        is_bot_started
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        chat_id,
                        CLEANUP_THRESHOLDS["MAX_SUMMARY_LENGTH"],
                        "es",
                        False,
                        50,
                        CLEANUP_THRESHOLDS["DAYS_TO_KEEP"],
                        CLEANUP_THRESHOLDS["MINIMUM_MESSAGES"],
                        CLEANUP_THRESHOLDS["CLEANUP_THRESHOLD"],
                        False,
                    ),
                )
                config = await self.fetch_one(query, (chat_id,))
            return dict(config)
        except Exception as e:
            logger.error(f"Error getting chat config: {e}")
            raise

    async def update_chat_config(self, chat_id: int, updates: Dict) -> Optional[Dict]:
        """Update chat configuration"""
        try:
            # Get current timestamp
            current_time = datetime.utcnow()

            # Build update query dynamically based on provided updates
            valid_fields = {
                "max_summary_length": int,
                "language": str,
                "auto_summarize": bool,
                "auto_summarize_threshold": int,
                "cleanup_days": int,
                "cleanup_min_messages": int,
                "cleanup_threshold": int,
            }

            # Validate and filter updates
            filtered_updates = {}
            for key, value in updates.items():
                if key in valid_fields:
                    try:
                        # Convert value to expected type
                        filtered_updates[key] = valid_fields[key](value)
                    except ValueError as e:
                        logger.warning(f"Invalid value for {key}: {value}")
                        continue

            if not filtered_updates:
                logger.warning("No valid updates provided")
                return None

            # Build and execute update query
            set_clause = ", ".join(f"{k} = ?" for k in filtered_updates.keys())
            query = f"""
                UPDATE chat_config
                SET {set_clause}, updated_at = ?
                WHERE chat_id = ?
            """

            values = list(filtered_updates.values()) + [current_time, chat_id]
            await self.execute(query, values)

            # Return updated config
            return await self.get_chat_config(chat_id)
        except Exception as e:
            logger.error(f"Error updating chat config: {e}")
            raise

    async def __aenter__(self):
        if not self.conn:
            await self.initialize(self.db_path)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


db_service = DatabaseService()  # Single instance
