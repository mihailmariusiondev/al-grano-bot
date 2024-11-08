import aiosqlite
from typing import Optional, List, Dict, Tuple
from ..utils.logger import logger
from utils.constants import CLEANUP_THRESHOLDS


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

    async def initialize(self, db_path: str = "bot.db"):
        """Initialize the database connection and create tables"""
        self.db_path = db_path
        try:
            self.conn = await aiosqlite.connect(db_path)
            await self._create_tables()
            self.logger.info(f"Database initialized at {db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    async def _create_tables(self):
        """Create the tables needed for the bot"""
        try:
            async with self.conn.cursor() as cursor:
                # Create TelegramUserEntity table
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telegram_user (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        usage_count INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create TelegramChatStateEntity table
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telegram_chat_state (
                        chat_id INTEGER PRIMARY KEY,
                        is_bot_started BOOLEAN DEFAULT FALSE,
                        last_command_usage INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create TelegramMessageEntity table
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telegram_message (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_text TEXT,
                        telegram_message_id INTEGER,
                        telegram_reply_to_message_id INTEGER,
                        chat_id INTEGER,
                        user_id INTEGER,
                        message_type TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (chat_id) REFERENCES telegram_chat_state (chat_id),
                        FOREIGN KEY (user_id) REFERENCES telegram_user (user_id)
                    )
                """
                )

                # Add chat settings table
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chat_settings (
                        chat_id INTEGER PRIMARY KEY,
                        max_summary_length INTEGER DEFAULT 2000,
                        language TEXT DEFAULT 'es',
                        auto_summarize BOOLEAN DEFAULT FALSE,
                        auto_summarize_threshold INTEGER DEFAULT 50,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                await self.conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to create tables: {e}")
            raise

    async def execute(self, query: str, params: tuple = ()) -> None:
        """Execute a query (INSERT, UPDATE, DELETE)"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        async with self.conn.cursor() as cursor:
            await cursor.execute(query, params)
            await self.conn.commit()

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

    async def is_premium_user(self, user_id: int) -> bool:
        """Check if a user has premium status"""
        try:
            user = await self.fetch_one(
                "SELECT is_premium FROM users WHERE user_id = ?", (user_id,)
            )
            return user["is_premium"] if user else False
        except Exception as e:
            self.logger.error(f"Error checking premium status for user {user_id}: {e}")
            return False

    @property
    def closed(self) -> bool:
        """Check if database connection is closed"""
        return self.conn is None or self.conn.closed

    async def get_chat_state(self, chat_id: int):
        """Get chat state"""
        try:
            return await self.fetch_one(
                "SELECT * FROM telegram_chat_state WHERE chat_id = ?", (chat_id,)
            )
        except Exception as e:
            self.logger.error(f"Error fetching chat state: {e}")
            return None

    async def save_chat_state(
        self, chat_id: int, is_bot_started: bool, last_command_usage: int
    ):
        """Save chat state"""
        try:
            await self.execute(
                """
                INSERT OR REPLACE INTO telegram_chat_state (chat_id, is_bot_started, last_command_usage)
                VALUES (?, ?, ?)
                """,
                (chat_id, is_bot_started, last_command_usage),
            )
            self.logger.info(f"Chat state saved for chat ID: {chat_id}")
        except Exception as e:
            self.logger.error(f"Error saving chat state: {e}")

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

    async def get_or_create_chat_state(self, chat_id: int):
        """Get chat state or create if not exists"""
        chat_state = await self.get_chat_state(chat_id)
        if chat_state:
            return chat_state
        else:
            await self.save_chat_state(chat_id, False, 0)
            return await self.get_chat_state(chat_id)

    async def update_chat_state(self, chat_id: int, updates: dict):
        """Update chat state"""
        try:
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE telegram_chat_state SET {set_clause} WHERE chat_id = ?"
            params = list(updates.values()) + [chat_id]
            await self.execute(query, tuple(params))
            self.logger.info(f"Chat state updated for chat ID: {chat_id}")
        except Exception as e:
            self.logger.error(f"Error updating chat state: {e}")

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

    async def get_cleanup_stats(self, chat_id: int) -> Tuple[int, str]:
        """Get message statistics for cleanup logging"""
        try:
            query = """
                SELECT
                    COUNT(*) as total_messages,
                    MIN(created_at) as oldest_message,
                    MAX(created_at) as newest_message
                FROM telegram_message
                WHERE chat_id = ?
            """
            stats = await self.fetch_one(query, (chat_id,))
            return (
                stats['total_messages'],
                f"oldest: {stats['oldest_message']}, newest: {stats['newest_message']}"
            )
        except Exception as e:
            logger.error(f"Error getting cleanup stats: {e}")
            return (0, "unknown")

    async def cleanup_old_messages(
        self,
        chat_id: int,
        days: int = CLEANUP_THRESHOLDS['DAYS_TO_KEEP'],
        keep_minimum: int = CLEANUP_THRESHOLDS['MINIMUM_MESSAGES']
    ) -> None:
        """
        Delete messages older than specified days while keeping minimum number of messages.

        Args:
            chat_id: The chat ID to cleanup
            days: Number of days of messages to keep
            keep_minimum: Minimum number of messages to retain
        """
        try:
            # Log initial state
            initial_count, time_range = await self.get_cleanup_stats(chat_id)
            logger.info(
                f"Starting cleanup for chat {chat_id}:\n"
                f"- Current messages: {initial_count}\n"
                f"- Time range: {time_range}"
            )

            if initial_count <= keep_minimum:
                logger.info(
                    f"Skipping cleanup for chat {chat_id}: "
                    f"message count ({initial_count}) <= minimum ({keep_minimum})"
                )
                return

            # Begin transaction
            async with self.connection:
                # First, ensure we keep the minimum number of recent messages
                keep_ids_query = """
                    WITH RankedMessages AS (
                        SELECT id,
                            ROW_NUMBER() OVER (
                                PARTITION BY chat_id
                                ORDER BY created_at DESC
                            ) as rn
                        FROM telegram_message
                        WHERE chat_id = ?
                    )
                    SELECT id
                    FROM RankedMessages
                    WHERE rn <= ?
                """

                # Then delete old messages except the kept ones
                delete_query = """
                    DELETE FROM telegram_message
                    WHERE chat_id = ?
                    AND created_at < datetime('now', '-? days')
                    AND id NOT IN (
                        WITH RankedMessages AS (
                            SELECT id,
                                ROW_NUMBER() OVER (
                                    PARTITION BY chat_id
                                    ORDER BY created_at DESC
                                ) as rn
                            FROM telegram_message
                            WHERE chat_id = ?
                        )
                        SELECT id
                        FROM RankedMessages
                        WHERE rn <= ?
                    )
                """

                # Execute the deletion
                result = await self.execute(
                    delete_query,
                    (chat_id, days, chat_id, keep_minimum)
                )

                # Get final state
                final_count, new_time_range = await self.get_cleanup_stats(chat_id)
                deleted_count = initial_count - final_count

                # Log cleanup results
                logger.info(
                    f"Cleanup completed for chat {chat_id}:\n"
                    f"- Messages deleted: {deleted_count}\n"
                    f"- Initial count: {initial_count}\n"
                    f"- Final count: {final_count}\n"
                    f"- New time range: {new_time_range}"
                )

                # Warn if cleanup might need adjustment
                if deleted_count == 0:
                    logger.warning(
                        f"No messages were deleted in chat {chat_id}. "
                        f"Consider adjusting cleanup parameters."
                    )
                elif final_count < keep_minimum:
                    logger.warning(
                        f"Final message count ({final_count}) is below minimum "
                        f"({keep_minimum}) for chat {chat_id}"
                    )

        except Exception as e:
            logger.error(
                f"Error during cleanup for chat {chat_id}: {str(e)}",
                exc_info=True
            )
            raise

    async def update_usage_stats(self, user_id: int, command: str) -> None:
        """Track command usage statistics"""
        try:
            query = """
                INSERT INTO command_stats (user_id, command_name, usage_count)
                VALUES (?, ?, 1)
                ON CONFLICT (user_id, command_name)
                DO UPDATE SET usage_count = usage_count + 1
            """
            await self.execute(query, (user_id, command))
        except Exception as e:
            logger.error(f"Error updating usage stats: {e}")
            raise

    async def get_message_count(self, chat_id: int) -> int:
        """Get total message count for a chat"""
        try:
            query = "SELECT COUNT(*) as count FROM telegram_message WHERE chat_id = ?"
            result = await self.fetch_one(query, (chat_id,))
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            raise

    async def get_all_chats(self) -> List[Dict]:
        """Get all unique chat IDs"""
        try:
            query = "SELECT DISTINCT chat_id FROM chat_state"
            return await self.fetch_all(query)
        except Exception as e:
            logger.error(f"Error getting chats: {e}")
            raise


db_service = DatabaseService()  # Single instance
