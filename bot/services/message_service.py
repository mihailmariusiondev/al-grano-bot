from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from telegram.constants import MessageLimit
from bot.utils.logger import logger
import asyncio

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
    ) -> bool:
        """Send a message to a chat, handling long messages and errors.

        Args:
            chat_id: The chat ID to send the message to
            text: The message text
            parse_mode: Optional parse mode (Markdown, HTML)

        Returns:
            True if the message was sent successfully, False otherwise
        """
        if not self.bot:
            logger.error("Message service not initialized with bot instance")
            return False

        try:
            # Check if the message is too long
            if len(text) > MessageLimit.MAX_TEXT_LENGTH:
                return await self.send_long_message(chat_id, text, parse_mode)
            else:
                await self.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
            return True
        except TelegramError as e:
            logger.error(f"Error sending message to chat {chat_id}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message to chat {chat_id}: {e}", exc_info=True)
            return False

    async def send_long_message(
        self, chat_id: int, text: str, parse_mode: Optional[str] = None
    ) -> bool:
        """Split and send a long message.

        Args:
            chat_id: The chat ID to send the message to
            text: The long message text
            parse_mode: Optional parse mode (Markdown, HTML)

        Returns:
            True if all parts were sent successfully, False otherwise
        """
        if not self.bot:
            logger.error("Message service not initialized with bot instance")
            return False

        try:
            # Split the message into chunks of 4000 characters (leaving room for markers)
            max_chunk_size = 4000
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

            # Send each chunk with a part indicator
            for i, chunk in enumerate(chunks):
                part_indicator = f"[Parte {i+1}/{len(chunks)}]\n" if len(chunks) > 1 else ""
                message_text = f"{part_indicator}{chunk}"

                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    parse_mode=parse_mode
                )

                # Add pause between chunks to avoid rate limiting
                if i < len(chunks) - 1:  # Don't pause after the last chunk
                    await asyncio.sleep(0.5)

            return True
        except TelegramError as e:
            logger.error(f"Error sending long message to chat {chat_id}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending long message to chat {chat_id}: {e}", exc_info=True)
            return False


# Single instance for import
message_service = MessageService()
