import os
from typing import Optional, List, Set


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

            # Auto Admin IDs
            self.AUTO_ADMIN_USER_IDS: Set[int] = set()

            self.initialized = True

    def load_from_env(self):
        """Load configuration from environment variables"""
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.DB_PATH = os.getenv("DB_PATH", "bot.db")

        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

        # Load Auto Admin IDs from environment variable
        auto_admin_ids_str = os.getenv("AUTO_ADMIN_USER_IDS_CSV")
        if auto_admin_ids_str:
            try:
                self.AUTO_ADMIN_USER_IDS = {
                    int(uid.strip()) for uid in auto_admin_ids_str.split(',') if uid.strip()
                }
            except ValueError:
                print(f"WARNING: Invalid format for AUTO_ADMIN_USER_IDS_CSV: '{auto_admin_ids_str}'. Expected comma-separated integers.")
                self.AUTO_ADMIN_USER_IDS = set()
        else:
            # Optional: Add default admin ID if no environment variable is set
            # Uncomment and replace with your actual ID if desired
            # NOTE: This is the ID of the bot owner
            self.AUTO_ADMIN_USER_IDS.add(6025856)
            pass


config = Config()  # Single instance
