import aiosqlite
from typing import Optional, List, Dict
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
        """Create the basic tables needed for the bot"""
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_premium BOOLEAN DEFAULT FALSE
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


db_service = DatabaseService()  # Single instance
