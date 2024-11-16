import os
from typing import Optional, List


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            # Bot settings
            self.BOT_TOKEN: Optional[str] = None
            self.OPENAI_API_KEY: Optional[str] = None

            # Database settings
            self.DB_PATH: str = "bot.db"

            # Other settings
            self.DEBUG_MODE: bool = False
            self.ENVIRONMENT: str = "development"

            self.initialized = True

    def load_from_env(self):
        """Load configuration from environment variables"""
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.DB_PATH = os.getenv("DB_PATH", "bot.db")

        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


config = Config()  # Single instance
