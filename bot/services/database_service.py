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

    @property
    def closed(self) -> bool:
        """Check if database connection is closed"""
        return self.conn is None or self.conn.closed

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

        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(query, params)
                if auto_commit:
                    await self.conn.commit()
                    self.logger.debug(f"Query executed and committed: {query}")
                else:
                    self.logger.debug(f"Query executed without commit: {query}")
        except Exception as e:
            self.logger.error(f"Error executing query: {query}, error: {str(e)}")
            if auto_commit:
                await self.conn.rollback()
                self.logger.debug("Transaction rolled back")
            raise

    async def execute_many(
        self, query: str, params_list: List[tuple], auto_commit: bool = True
    ) -> None:
        """Execute multiple queries in a batch"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        try:
            async with self.conn.cursor() as cursor:
                await cursor.executemany(query, params_list)
                if auto_commit:
                    await self.conn.commit()
                    self.logger.debug(f"Batch query executed and committed: {query}")
                else:
                    self.logger.debug(f"Batch query executed without commit: {query}")
        except Exception as e:
            self.logger.error(f"Error executing batch query: {query}, error: {str(e)}")
            if auto_commit:
                await self.conn.rollback()
                self.logger.debug("Transaction rolled back")
            raise

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
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Dict:
        """Get existing user or create new one"""
        try:
            # Get existing user
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM telegram_user WHERE user_id = ?", (user_id,)
                )
                existing_user = await cursor.fetchone()

            if existing_user:
                existing_user = dict(existing_user)
                # Compare existing values with new values safely
                needs_update = False
                update_fields = []
                update_values = []

                # Helper function to compare values safely
                def values_different(old_val, new_val) -> bool:
                    if old_val is None and new_val is None:
                        return False
                    return old_val != new_val

                # Check each field for updates
                if values_different(existing_user["username"], username):
                    update_fields.append("username = ?")
                    update_values.append(username)
                    needs_update = True

                if values_different(existing_user["first_name"], first_name):
                    update_fields.append("first_name = ?")
                    update_values.append(first_name)
                    needs_update = True

                if values_different(existing_user["last_name"], last_name):
                    update_fields.append("last_name = ?")
                    update_values.append(last_name)
                    needs_update = True

                # Update user if needed
                if needs_update:
                    update_values.append(user_id)  # Add user_id for WHERE clause
                    update_query = f"""
                        UPDATE telegram_user
                        SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """
                    await self.execute(update_query, tuple(update_values))
                    self.logger.info(
                        f"User {user_id} updated with fields: {', '.join(update_fields)}"
                    )

                    # Fetch updated user data
                    async with self.conn.cursor() as cursor:
                        await cursor.execute(
                            "SELECT * FROM telegram_user WHERE user_id = ?", (user_id,)
                        )
                        return dict(await cursor.fetchone())

                return existing_user

            else:
                # Create new user
                insert_query = """
                    INSERT INTO telegram_user (
                        user_id, username, first_name, last_name
                    ) VALUES (?, ?, ?, ?)
                """
                await self.execute(
                    insert_query, (user_id, username, first_name, last_name)
                )
                self.logger.info(f"New user created: {user_id}")

                # Fetch and return the newly created user
                async with self.conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT * FROM telegram_user WHERE user_id = ?", (user_id,)
                    )
                    return dict(await cursor.fetchone())

        except Exception as e:
            self.logger.error(f"Error in get_or_create_user: {e}")
            raise

    async def get_user(self, user_id: int):
        """Get user"""
        try:
            return await self.fetch_one(
                "SELECT * FROM telegram_user WHERE user_id = ?", (user_id,)
            )
        except Exception as e:
            self.logger.error(f"Error fetching user: {e}")
            return None

    async def get_chat_config(self, chat_id: int) -> Optional[Dict]:
        """Get chat configuration or create default if not exists"""
        try:
            # Try to get existing config
            query = "SELECT * FROM chat_config WHERE chat_id = ?"
            async with self.conn.cursor() as cursor:
                await cursor.execute(query, (chat_id,))
                result = await cursor.fetchone()

                if result:
                    return dict(result)

                # Create default config if not exists
                default_config = {
                    "chat_id": chat_id,
                    "max_summary_length": CLEANUP_THRESHOLDS["MAX_SUMMARY_LENGTH"],
                    "language": "es",
                    "auto_summarize": False,
                    "auto_summarize_threshold": 50,
                    "cleanup_days": CLEANUP_THRESHOLDS["DAYS_TO_KEEP"],
                    "cleanup_min_messages": CLEANUP_THRESHOLDS["MINIMUM_MESSAGES"],
                    "cleanup_threshold": CLEANUP_THRESHOLDS["CLEANUP_THRESHOLD"],
                    "is_bot_started": False,
                }

                columns = ", ".join(default_config.keys())
                placeholders = ", ".join("?" * len(default_config))
                query = f"INSERT INTO chat_config ({columns}) VALUES ({placeholders})"

                await self.execute(query, tuple(default_config.values()))
                return default_config

        except Exception as e:
            self.logger.error(f"Error getting/creating chat config: {e}")
            raise

    async def update_chat_config(self, chat_id: int, updates: Dict) -> Optional[Dict]:
        """Update chat configuration"""
        try:
            # Get current timestamp
            current_time = datetime.utcnow()

            # Define valid fields and their types
            valid_fields = {
                "max_summary_length": int,
                "language": str,
                "auto_summarize": bool,
                "auto_summarize_threshold": int,
                "cleanup_days": int,
                "cleanup_min_messages": int,
                "cleanup_threshold": int,
                "is_bot_started": bool,  # Added missing field
            }

            # Validate and filter updates
            valid_updates = {}
            for key, value in updates.items():
                if key not in valid_fields:
                    self.logger.warning(f"Invalid configuration field: {key}")
                    continue

                # Type validation and conversion
                expected_type = valid_fields[key]
                try:
                    if expected_type == bool and isinstance(value, str):
                        value = value.lower() == "true"
                    else:
                        value = expected_type(value)
                    valid_updates[key] = value
                except (ValueError, TypeError) as e:
                    self.logger.error(
                        f"Invalid value for {key}: {value}. Expected {expected_type}"
                    )
                    continue

            if not valid_updates:
                self.logger.warning("No valid updates provided")
                return None

            # Build update query
            update_fields = [f"{key} = ?" for key in valid_updates.keys()]
            update_values = list(valid_updates.values())
            query = f"""
                UPDATE chat_config
                SET {', '.join(update_fields)}, updated_at = ?
                WHERE chat_id = ?
            """

            # Execute update
            await self.execute(query, tuple(update_values + [current_time, chat_id]))

            # Return updated configuration
            return await self.get_chat_config(chat_id)

        except Exception as e:
            self.logger.error(f"Error updating chat config: {e}")
            raise

    async def __aenter__(self):
        if not self.conn:
            await self.initialize(self.db_path)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def transaction(self):
        """Context manager for handling transactions"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        tr = await self.conn.cursor()
        try:
            yield tr
            await self.conn.commit()
        except Exception:
            await self.conn.rollback()
            raise
        finally:
            await tr.close()


db_service = DatabaseService()  # Single instance
