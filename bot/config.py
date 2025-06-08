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
            self.OPENAI_API_KEY: Optional[str] = None # For direct OpenAI calls (e.g., Whisper)
            self.OPENROUTER_API_KEY: Optional[str] = None # For OpenRouter LLM calls
            self.OPENROUTER_SITE_URL: str = "https://github.com/mihailmariusiondev/al-grano-bot" # Default or example URL
            self.OPENROUTER_SITE_NAME: str = "Al-Grano Bot" # Default or example name
            self.OPENROUTER_PRIMARY_MODEL: str = "deepseek/deepseek-r1-0528-qwen3-8b:free" # Updated primary model
            self.OPENROUTER_FALLBACK_MODEL: str = "deepseek/deepseek-r1-0528-qwen3-8b" # Updated fallback model
            # Database settings
            self.DB_PATH: str = "bot.db"
            # Other settings
            # Auto Admin IDs
            self.AUTO_ADMIN_USER_IDS: Set[int] = set()
            self.initialized = True

    def load_from_env(self):
        """Load configuration from environment variables"""
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        self.OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", self.OPENROUTER_SITE_URL)
        self.OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", self.OPENROUTER_SITE_NAME)
        # Load model identifiers from env, with defaults
        self.OPENROUTER_PRIMARY_MODEL = os.getenv("OPENROUTER_PRIMARY_MODEL", self.OPENROUTER_PRIMARY_MODEL) # Default is now the new model
        self.OPENROUTER_FALLBACK_MODEL = os.getenv("OPENROUTER_FALLBACK_MODEL", self.OPENROUTER_FALLBACK_MODEL) # Default is now the new model
        self.DB_PATH = os.getenv("DB_PATH", "bot.db")
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
            self.AUTO_ADMIN_USER_IDS.add(6025856) # Default admin ID

config = Config()  # Single instance
