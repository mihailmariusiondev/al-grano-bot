from typing import Optional
from bot.utils.logger import logger

logger = logger.get_logger(__name__)


class MessageService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            self.bot = None
            self.initialized = True

    def initialize(self, bot):
        """Initialize with bot instance"""
        self.bot = bot

    async def send_message(
        self, chat_id: int, text: str, parse_mode: Optional[str] = None
    ):
        """Send message using bot instance"""
        if not self.bot:
            raise RuntimeError("Message service not initialized with bot instance")

        try:
            await self.bot.send_message(
                chat_id=chat_id, text=text, parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"Error sending message to chat {chat_id}: {e}", exc_info=True)
            raise


message_service = MessageService()  # Single instance
