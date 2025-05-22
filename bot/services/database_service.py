import aiosqlite
from typing import Optional, List, Dict

from bot.utils.constants import MAX_RECENT_MESSAGES
from ..utils.logger import logger


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
        return self.conn is None

    async def initialize(self, db_path: str = "bot.db"):
        """Initialize database connection and create tables"""
        try:
            self.db_path = db_path
            self.conn = await aiosqlite.connect(db_path)
            self.conn.row_factory = aiosqlite.Row

            # Add columns if they don't exist
            try:
                await self.conn.execute(
                    """
                    ALTER TABLE telegram_chat_state
                    ADD COLUMN daily_summary_enabled BOOLEAN DEFAULT FALSE
                    """
                )
            except aiosqlite.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise

            try:
                await self.conn.execute(
                    """
                    ALTER TABLE telegram_chat_state
                    ADD COLUMN summary_type TEXT DEFAULT 'long'
                    """
                )
            except aiosqlite.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise

            # Create tables
            await self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_user (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_premium BOOLEAN DEFAULT FALSE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    last_text_summary_time TIMESTAMP NULL,
                    last_media_summary_time TIMESTAMP NULL,
                    media_summary_daily_count INTEGER DEFAULT 0,
                    media_summary_last_reset TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Add new columns to telegram_user if they don't exist
            try:
                await self.conn.execute(
                    "ALTER TABLE telegram_user ADD COLUMN last_text_summary_time TIMESTAMP NULL"
                )
                await self.conn.commit()
            except aiosqlite.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
            try:
                await self.conn.execute(
                    "ALTER TABLE telegram_user ADD COLUMN last_media_summary_time TIMESTAMP NULL"
                )
                await self.conn.commit()
            except aiosqlite.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
            try:
                await self.conn.execute(
                    "ALTER TABLE telegram_user ADD COLUMN media_summary_daily_count INTEGER DEFAULT 0"
                )
                await self.conn.commit()
            except aiosqlite.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
            try:
                await self.conn.execute(
                    "ALTER TABLE telegram_user ADD COLUMN media_summary_last_reset TIMESTAMP NULL"
                )
                await self.conn.commit()
            except aiosqlite.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise

            # Crear trigger para actualizar 'updated_at' automáticamente en telegram_user
            await self.conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_telegram_user_updated_at
                AFTER UPDATE ON telegram_user
                FOR EACH ROW
                BEGIN
                    UPDATE telegram_user SET updated_at = CURRENT_TIMESTAMP WHERE user_id = OLD.user_id;
                END;
                """
            )
            await self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_chat_state (
                    chat_id INTEGER PRIMARY KEY,
                    is_bot_started BOOLEAN DEFAULT FALSE,
                    last_command_usage TIMESTAMP NULL,
                    daily_summary_enabled BOOLEAN DEFAULT FALSE,
                    summary_type TEXT DEFAULT 'long',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            # Crear trigger para actualizar 'updated_at' automáticamente en telegram_chat_state
            await self.conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_telegram_chat_state_updated_at
                AFTER UPDATE ON telegram_chat_state
                FOR EACH ROW
                BEGIN
                    UPDATE telegram_chat_state SET updated_at = CURRENT_TIMESTAMP WHERE chat_id = OLD.chat_id;
                END;
                """
            )
            await self.conn.execute(
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
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES telegram_chat_state(chat_id),
                    FOREIGN KEY (user_id) REFERENCES telegram_user(user_id)
                )
            """
            )
            # Crear trigger para actualizar 'updated_at' automáticamente en telegram_message
            await self.conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_telegram_message_updated_at
                AFTER UPDATE ON telegram_message
                FOR EACH ROW
                BEGIN
                    UPDATE telegram_message SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                END;
                """
            )
            # Crear trigger para limpiar mensajes antiguos después de insertar uno nuevo
            await self.conn.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS cleanup_old_messages
                AFTER INSERT ON telegram_message
                BEGIN
                    DELETE FROM telegram_message
                    WHERE chat_id = NEW.chat_id
                    AND id NOT IN (
                        SELECT id FROM telegram_message
                        WHERE chat_id = NEW.chat_id
                        ORDER BY telegram_message_id DESC
                        LIMIT {MAX_RECENT_MESSAGES}
                    );
                END;
                """
            )
            await self.conn.commit()
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
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

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch a single row from the database"""
        if not self.conn:
            raise RuntimeError("Database not initialized")
        async with self.conn.execute(query, params) as cursor:
            result = await cursor.fetchone()
            return dict(result) if result else None

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows from the database"""
        if not self.conn:
            raise RuntimeError("Database not initialized")
        async with self.conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

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

    async def get_recent_messages(self, chat_id: int, limit: int = 300) -> List[Dict]:
        """Get recent messages from a chat"""
        try:
            query = """
                SELECT m.message_text, m.telegram_message_id, m.telegram_reply_to_message_id,
                       u.user_id, u.first_name, u.last_name, u.username
                FROM telegram_message m
                JOIN telegram_user u ON m.user_id = u.user_id
                WHERE m.chat_id = ?
                ORDER BY m.telegram_message_id DESC
                LIMIT ?
            """
            messages = await self.fetch_all(query, (chat_id, limit))
            return messages
        except Exception as e:
            self.logger.error(f"Error getting recent messages: {e}")
            raise

    async def save_message(
        self,
        chat_id: int,
        user_id: int,
        message_text: str,
        telegram_message_id: int,
        telegram_reply_to_message_id: Optional[int],
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
            user = await self.fetch_one(
                "SELECT * FROM telegram_user WHERE user_id = ?", (user_id,)
            )
            if user:
                # Compare existing values with new values safely
                needs_update = False
                update_fields = []
                update_values = []

                # Helper function to compare values safely
                def values_different(old_val, new_val) -> bool:
                    if old_val is None and new_val is None:
                        return False
                    return old_val != new_val

                # Check cada campo para actualizaciones
                if values_different(user["username"], username):
                    update_fields.append("username = ?")
                    update_values.append(username)
                    needs_update = True
                if values_different(user["first_name"], first_name):
                    update_fields.append("first_name = ?")
                    update_values.append(first_name)
                    needs_update = True
                if values_different(user["last_name"], last_name):
                    update_fields.append("last_name = ?")
                    update_values.append(last_name)
                    needs_update = True

                # Actualizar usuario si es necesario
                if needs_update:
                    update_values.append(
                        user_id
                    )  # Añadir user_id para la cláusula WHERE
                    update_query = f"""
                        UPDATE telegram_user
                        SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """
                    await self.execute(update_query, tuple(update_values))
                    self.logger.info(
                        f"User {user_id} updated with fields: {', '.join(update_fields)}"
                    )
                    # Obtener datos actualizados del usuario
                    user = await self.fetch_one(
                        "SELECT * FROM telegram_user WHERE user_id = ?", (user_id,)
                    )
                return user
            else:
                # Crear nuevo usuario
                insert_query = """
                    INSERT INTO telegram_user (
                        user_id, username, first_name, last_name,
                        last_text_summary_time, last_media_summary_time,
                        media_summary_daily_count, media_summary_last_reset
                    ) VALUES (?, ?, ?, ?, NULL, NULL, 0, CURRENT_TIMESTAMP)
                """
                await self.execute(
                    insert_query, (user_id, username, first_name, last_name)
                )
                self.logger.info(f"New user created: {user_id}")
                # Obtener y retornar el usuario recién creado
                user = await self.fetch_one(
                    "SELECT * FROM telegram_user WHERE user_id = ?", (user_id,)
                )
                return user
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

    async def get_chat_state(self, chat_id: int) -> dict:
        """Get chat state, create if not exists"""
        try:
            chat = await self.fetch_one(
                "SELECT * FROM telegram_chat_state WHERE chat_id = ?", (chat_id,)
            )
            if not chat:
                # Inicializar con last_command_usage como NULL
                await self.execute(
                    """
                    INSERT INTO telegram_chat_state
                    (chat_id, is_bot_started, last_command_usage)
                    VALUES (?, ?, NULL)
                    """,
                    (chat_id, False),
                )
                chat = await self.fetch_one(
                    "SELECT * FROM telegram_chat_state WHERE chat_id = ?", (chat_id,)
                )
            return chat
        except Exception as e:
            self.logger.error(f"Error in get_chat_state: {e}")
            raise

    async def update_chat_state(self, chat_id: int, state: dict) -> dict:
        """Update chat state"""
        try:
            set_clause = ", ".join([f"{k} = ?" for k in state.keys()])
            values = list(state.values()) + [chat_id]
            await self.execute(
                f"""
                UPDATE telegram_chat_state
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE chat_id = ?
                """,
                values,
            )
            return await self.get_chat_state(chat_id)
        except Exception as e:
            self.logger.error(f"Error updating chat state: {e}")
            raise

    async def __aenter__(self):
        if not self.conn:
            await self.initialize(self.db_path or "bot.db")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_admin_users(self) -> List[int]:
        """Fetch admin user IDs from the database."""
        try:
            rows = await self.fetch_all(
                "SELECT user_id FROM telegram_user WHERE is_admin = 1"
            )
            return [row["user_id"] for row in rows]
        except Exception as e:
            self.logger.error(f"Error fetching admin users: {e}")
            return []

    async def update_user_summary_rate_limit_data(
        self,
        user_id: int,
        last_text_summary_time: Optional[str] = None,
        last_media_summary_time: Optional[str] = None,
        media_summary_daily_count: Optional[int] = None,
        media_summary_last_reset: Optional[str] = None,
    ):
        if not self.conn:
            raise RuntimeError("Database not initialized")

        fields_to_update = []
        params = []

        if last_text_summary_time is not None:
            fields_to_update.append("last_text_summary_time = ?")
            params.append(last_text_summary_time)
        if last_media_summary_time is not None:
            fields_to_update.append("last_media_summary_time = ?")
            params.append(last_media_summary_time)
        if media_summary_daily_count is not None:
            fields_to_update.append("media_summary_daily_count = ?")
            params.append(media_summary_daily_count)
        if media_summary_last_reset is not None:
            fields_to_update.append("media_summary_last_reset = ?")
            params.append(media_summary_last_reset)

        if not fields_to_update:
            self.logger.info(f"No fields to update for user {user_id} in update_user_summary_rate_limit_data")
            return

        query = f"UPDATE telegram_user SET {', '.join(fields_to_update)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
        params.append(user_id)

        try:
            await self.execute(query, tuple(params))
            self.logger.info(f"Successfully updated rate limit data for user {user_id}. Fields: {fields_to_update}")
        except Exception as e:
            self.logger.error(f"Error updating rate limit data for user {user_id}: {e}")
            # Potentially re-raise or handle as appropriate
            raise


db_service = DatabaseService()  # Single instance
