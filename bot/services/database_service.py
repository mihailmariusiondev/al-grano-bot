import aiosqlite
from datetime import datetime
import pytz
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import pytz
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
        self.logger.debug(f"=== DATABASE INITIALIZATION STARTED ===")
        self.logger.debug(f"Database path: {db_path}")

        try:
            self.db_path = db_path
            self.conn = await aiosqlite.connect(db_path)
            self.conn.row_factory = aiosqlite.Row

            self.logger.info(f"Database connection established: {db_path}")

            # Create tables
            await self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_user (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    last_text_simple_op_time TIMESTAMP NULL,
                    last_advanced_op_time TIMESTAMP NULL,
                    advanced_op_today_count INTEGER NOT NULL DEFAULT 0,
                    advanced_op_count_reset_date DATE NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
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
                    # Log or ignore if the table might not exist yet,
                    # but for now, we'll re-raise if it's not a duplicate column error
                    pass # Or self.logger.warning("Could not add daily_summary_enabled, table might not exist or other issue.")

            try:
                await self.conn.execute(
                    """
                    ALTER TABLE telegram_chat_state
                    ADD COLUMN summary_type TEXT DEFAULT 'long'
                    """
                )
            except aiosqlite.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    # Similar handling as above
                    pass # Or self.logger.warning("Could not add summary_type, table might not exist or other issue.")

            # Add new columns to telegram_user if they don't exist
            user_columns_to_add = {
                "last_text_simple_op_time": "TIMESTAMP NULL",
                "last_advanced_op_time": "TIMESTAMP NULL",
                "advanced_op_today_count": "INTEGER NOT NULL DEFAULT 0",
                "advanced_op_count_reset_date": "DATE NULL",
            }

            for col_name, col_type in user_columns_to_add.items():
                try:
                    await self.conn.execute(
                        f"ALTER TABLE telegram_user ADD COLUMN {col_name} {col_type}"
                    )
                    self.logger.info(f"Added column {col_name} to telegram_user table.")
                except aiosqlite.OperationalError as e:
                    if "duplicate column" not in str(e).lower():
                        self.logger.warning(f"Could not add column {col_name} to telegram_user: {e}")
                    else:  # Column already exists
                        pass

            # Create chat_summary_config table
            await self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_summary_config (
                    chat_id             INTEGER PRIMARY KEY,
                    tone                TEXT    NOT NULL DEFAULT 'neutral',
                    length              TEXT    NOT NULL DEFAULT 'medium',
                    language            TEXT    NOT NULL DEFAULT 'es',
                    include_names       BOOLEAN NOT NULL DEFAULT 1,
                    daily_summary_hour  TEXT    NOT NULL DEFAULT 'off',
                    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create trigger for chat_summary_config updated_at
            await self.conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_chat_summary_config_updated_at
                AFTER UPDATE ON chat_summary_config
                FOR EACH ROW
                BEGIN
                    UPDATE chat_summary_config SET updated_at = CURRENT_TIMESTAMP WHERE chat_id = OLD.chat_id;
                END;
                """
            )

            # Migration logic: transfer existing configuration from telegram_chat_state
            try:
                # Check if there are any existing configurations to migrate
                existing_configs = await self.conn.execute(
                    """
                    SELECT chat_id, summary_type, daily_summary_enabled
                    FROM telegram_chat_state
                    WHERE summary_type IS NOT NULL OR daily_summary_enabled IS NOT NULL
                    """
                )
                rows = await existing_configs.fetchall()

                if rows:
                    self.logger.info(f"Migrating {len(rows)} existing chat configurations...")

                    for row in rows:
                        chat_id = row[0]
                        summary_type = row[1] if row[1] else 'medium'
                        daily_summary_enabled = row[2] if row[2] else False

                        # Map old summary_type to new length
                        length = 'short' if summary_type == 'short' else 'long'
                        daily_hour = '03' if daily_summary_enabled else 'off'

                        # Insert into new table (ignore if already exists)
                        await self.conn.execute(
                            """
                            INSERT OR IGNORE INTO chat_summary_config(
                                chat_id, tone, length, language, include_names, daily_summary_hour
                            ) VALUES (?, 'neutral', ?, 'es', 1, ?)
                            """,
                            (chat_id, length, daily_hour)
                        )

                    self.logger.info("Migration completed successfully")
            except Exception as e:
                self.logger.warning(f"Migration from old schema failed (this is normal for new installations): {e}")

            await self.conn.commit()
            self.logger.info("=== DATABASE INITIALIZATION COMPLETED SUCCESSFULLY ===")
            self.logger.debug(f"All tables and triggers created/verified")
        except Exception as e:
            self.logger.error(f"=== DATABASE INITIALIZATION FAILED ===")
            self.logger.error(f"Database initialization error: {e}", exc_info=True)
            raise

    async def execute(
        self, query: str, params: tuple = (), auto_commit: bool = True
    ) -> None:
        """Execute a query (INSERT, UPDATE, DELETE)"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        # Log query details
        query_type = query.strip().split()[0].upper()
        self.logger.debug(f"=== DATABASE EXECUTE: {query_type} ===")
        self.logger.debug(f"Query: {query}")
        self.logger.debug(f"Params: {params}")
        self.logger.debug(f"Auto commit: {auto_commit}")

        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(query, params)
                rows_affected = cursor.rowcount

                if auto_commit:
                    await self.conn.commit()
                    self.logger.debug(f"Query executed and committed. Rows affected: {rows_affected}")
                else:
                    self.logger.debug(f"Query executed without commit. Rows affected: {rows_affected}")

        except Exception as e:
            self.logger.error(f"Database query failed - Type: {query_type}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            self.logger.error(f"Error: {str(e)}", exc_info=True)
            if auto_commit:
                await self.conn.rollback()
                self.logger.debug("Transaction rolled back")
            raise

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch a single row from the database"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        self.logger.debug(f"=== DATABASE FETCH_ONE ===")
        self.logger.debug(f"Query: {query}")
        self.logger.debug(f"Params: {params}")

        try:
            async with self.conn.execute(query, params) as cursor:
                result = await cursor.fetchone()
                result_dict = dict(result) if result else None
                self.logger.debug(f"Result: {'Found 1 row' if result_dict else 'No rows found'}")
                return result_dict
        except Exception as e:
            self.logger.error(f"Database fetch_one failed")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            self.logger.error(f"Error: {str(e)}", exc_info=True)
            raise

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows from the database"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        self.logger.debug(f"=== DATABASE FETCH_ALL ===")
        self.logger.debug(f"Query: {query}")
        self.logger.debug(f"Params: {params}")

        try:
            async with self.conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                result_list = [dict(row) for row in rows]
                self.logger.debug(f"Result: Found {len(result_list)} rows")
                return result_list
        except Exception as e:
            self.logger.error(f"Database fetch_all failed")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Params: {params}")
            self.logger.error(f"Error: {str(e)}", exc_info=True)
            raise

    async def close(self):
        """Close the database connection"""
        if self.conn:
            await self.conn.close()
            self.logger.info("Database connection closed")
            self.conn = None

    async def get_recent_messages(self, chat_id: int, limit: int = 300, hours: int = None) -> List[Dict]:
        """Get recent messages from a chat.

        Args:
            chat_id: The chat ID
            limit: Maximum number of messages to retrieve
            hours: If provided, only get messages from the last N hours

        Returns:
            A list of message dictionaries with sender_name included
        """
        try:
            if hours is not None:
                # Get messages from the last N hours
                madrid_tz = pytz.timezone("Europe/Madrid")
                now = datetime.now(madrid_tz)
                start_time = now - timedelta(hours=hours)
                start_time_utc = start_time.astimezone(pytz.UTC)

                query = """
                    SELECT m.message_text, m.telegram_message_id, m.telegram_reply_to_message_id,
                           u.user_id, u.first_name, u.last_name, u.username, m.created_at
                    FROM telegram_message m
                    JOIN telegram_user u ON m.user_id = u.user_id
                    WHERE m.chat_id = ? AND m.created_at >= ?
                    ORDER BY m.telegram_message_id ASC
                    LIMIT ?
                """
                messages = await self.fetch_all(query, (chat_id, start_time_utc.isoformat(), limit))
            else:
                # Get the most recent messages up to the limit
                query = """
                    SELECT m.message_text, m.telegram_message_id, m.telegram_reply_to_message_id,
                           u.user_id, u.first_name, u.last_name, u.username, m.created_at
                    FROM telegram_message m
                    JOIN telegram_user u ON m.user_id = u.user_id
                    WHERE m.chat_id = ?
                    ORDER BY m.telegram_message_id DESC
                    LIMIT ?
                """
                messages = await self.fetch_all(query, (chat_id, limit))
                # Reverse to get chronological order
                messages.reverse()

            return messages
        except Exception as e:
            self.logger.error(f"Error getting recent messages: {e}")
            raise

    async def get_messages_for_date(self, chat_id: int, date) -> List[Dict]:
        """Get all messages for a specific date (00:00 - 23:59)"""
        try:
            madrid_tz = pytz.timezone("Europe/Madrid")
            day_start = datetime(
                date.year, date.month, date.day, 0, 0, 0, tzinfo=madrid_tz
            )
            day_end = day_start.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            day_start_utc = day_start.astimezone(pytz.UTC)
            day_end_utc = day_end.astimezone(pytz.UTC)

            self.logger.debug(f"=== GET_MESSAGES_FOR_DATE DEBUG ===")
            self.logger.debug(f"Input date: {date}")
            self.logger.debug(f"Madrid day_start: {day_start}")
            self.logger.debug(f"Madrid day_end: {day_end}")
            self.logger.debug(f"UTC day_start: {day_start_utc} ({day_start_utc.isoformat()})")
            self.logger.debug(f"UTC day_end: {day_end_utc} ({day_end_utc.isoformat()})")

            query = """
                SELECT m.message_text, m.created_at, m.telegram_message_id,
                       m.telegram_reply_to_message_id,
                       u.user_id, u.first_name, u.last_name, u.username
                FROM telegram_message m
                JOIN telegram_user u ON m.user_id = u.user_id
                WHERE m.chat_id = ?
                AND m.created_at BETWEEN ? AND ?
                ORDER BY m.telegram_message_id ASC
            """

            self.logger.debug(f"Query params: chat_id={chat_id}, start={day_start_utc.isoformat()}, end={day_end_utc.isoformat()}")

            messages = await self.fetch_all(
                query,
                (chat_id, day_start_utc.isoformat(), day_end_utc.isoformat()),
            )

            self.logger.debug(f"Messages found for date {date}: {len(messages)}")

            # Let's also check all messages for this chat to see what dates we have
            debug_query = """
                SELECT m.created_at, COUNT(*) as count
                FROM telegram_message m
                WHERE m.chat_id = ?
                GROUP BY DATE(m.created_at)
                ORDER BY m.created_at DESC
                LIMIT 10
            """
            debug_results = await self.fetch_all(debug_query, (chat_id,))
            self.logger.debug(f"Recent message dates in this chat: {debug_results}")

            return messages
        except Exception as e:
            self.logger.error(f"Error getting messages for date: {e}", exc_info=True)
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
                        last_text_simple_op_time, last_advanced_op_time,
                        advanced_op_today_count, advanced_op_count_reset_date
                    ) VALUES (?, ?, ?, ?, NULL, NULL, 0, NULL)
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
            self.logger.error(f"Error in get_or_create_user: {e}", exc_info=True)
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

    async def update_user_fields(self, user_id: int, fields_to_update: Dict) -> None:
        """Update specific fields for a user."""
        if not self.conn:
            raise RuntimeError("Database not initialized")
        if not fields_to_update:
            return

        set_clauses = [f"{key} = ?" for key in fields_to_update.keys()]
        params = list(fields_to_update.values()) + [user_id]

        query = f"""
            UPDATE telegram_user
            SET {", ".join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """
        try:
            await self.execute(query, tuple(params))
            self.logger.info(f"User {user_id} updated with fields: {', '.join(fields_to_update.keys())}")
        except Exception as e:
            self.logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
            raise

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

    async def get_chat_summary_config(self, chat_id: int) -> dict:
        """Get chat summary configuration, create with defaults if not exists.

        Args:
            chat_id: The chat ID

        Returns:
            Dictionary with configuration settings
        """
        try:
            config = await self.fetch_one(
                "SELECT * FROM chat_summary_config WHERE chat_id = ?", (chat_id,)
            )

            if not config:
                # Create default configuration
                default_config = {
                    'tone': 'neutral',
                    'length': 'medium',
                    'language': 'es',
                    'include_names': True,
                    'daily_summary_hour': 'off'
                }

                await self.execute(
                    """
                    INSERT INTO chat_summary_config (
                        chat_id, tone, length, language, include_names, daily_summary_hour
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chat_id,
                        default_config['tone'],
                        default_config['length'],
                        default_config['language'],
                        default_config['include_names'],
                        default_config['daily_summary_hour']
                    )
                )

                # Return the default configuration with chat_id
                config = default_config.copy()
                config['chat_id'] = chat_id
                self.logger.info(f"Created default summary config for chat {chat_id}")

            return dict(config)
        except Exception as e:
            self.logger.error(f"Error getting chat summary config for {chat_id}: {e}")
            raise

    async def update_chat_summary_config(self, chat_id: int, changes: dict) -> bool:
        """Update specific fields in chat summary configuration.

        Args:
            chat_id: The chat ID
            changes: Dictionary with fields to update

        Returns:
            True if update was successful, False otherwise
        """
        try:
            if not changes:
                return True

            # Ensure the config exists first
            await self.get_chat_summary_config(chat_id)

            # Build the update query
            set_clauses = [f"{key} = ?" for key in changes.keys()]
            params = list(changes.values()) + [chat_id]

            query = f"""
                UPDATE chat_summary_config
                SET {", ".join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                WHERE chat_id = ?
            """

            await self.execute(query, tuple(params))
            self.logger.info(f"Updated summary config for chat {chat_id}: {', '.join(changes.keys())}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating chat summary config for {chat_id}: {e}")
            return False

    async def get_all_daily_summary_configs(self) -> List[Dict]:
        """Get all chats with daily summaries enabled and their configurations.

        Returns:
            List of dicts with chat_id and daily_summary_hour for each configured chat
        """
        try:
            query = """
                SELECT chat_id, daily_summary_hour
                FROM chat_summary_config
                WHERE daily_summary_hour != 'off'
            """
            configs = await self.fetch_all(query)
            self.logger.info(f"Retrieved {len(configs)} daily summary configurations")
            return configs
        except Exception as e:
            self.logger.error(f"Error getting all daily summary configs: {e}")
            return []

    async def get_recent_messages_by_time(self, chat_id: int, hours: int = 24) -> List[Dict]:
        """Get recent messages from a chat within a specific time window.

        Args:
            chat_id: The chat ID
            hours: Number of hours to look back from now

        Returns:
            List of recent messages within the time window
        """
        try:
            from datetime import datetime, timedelta
            import pytz

            # Calculate the time window
            madrid_tz = pytz.timezone("Europe/Madrid")
            now = datetime.now(madrid_tz)
            start_time = now - timedelta(hours=hours)

            # Convert to UTC for database query
            start_time_utc = start_time.astimezone(pytz.UTC)
            now_utc = now.astimezone(pytz.UTC)

            query = """
                SELECT m.message_text, m.telegram_message_id, m.telegram_reply_to_message_id,
                       u.user_id, u.first_name, u.last_name, u.username, m.created_at
                FROM telegram_message m
                JOIN telegram_user u ON m.user_id = u.user_id
                WHERE m.chat_id = ?
                AND m.created_at BETWEEN ? AND ?
                ORDER BY m.telegram_message_id ASC
            """
            messages = await self.fetch_all(
                query,
                (chat_id, start_time_utc.isoformat(), now_utc.isoformat())
            )
            self.logger.info(f"Retrieved {len(messages)} messages from last {hours} hours for chat {chat_id}")
            return messages
        except Exception as e:
            self.logger.error(f"Error getting recent messages by time: {e}")
            return []

db_service = DatabaseService()  # Single instance
