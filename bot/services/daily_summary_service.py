from datetime import datetime, timedelta
import pytz
from typing import List, Dict
from bot.services.database_service import db_service
from bot.services.openai_service import openai_service
from bot.utils.format_utils import format_recent_messages
from bot.utils.logger import logger
from bot.services.message_service import message_service

logger = logger.get_logger(__name__)


async def get_yesterdays_messages(chat_id: int) -> List[Dict]:
    """
    Get messages from yesterday for a specific chat.
    Uses Europe/Madrid timezone.
    """
    try:
        # Get timezone
        madrid_tz = pytz.timezone("Europe/Madrid")
        now = datetime.now(madrid_tz)

        # Calculate yesterday's start and end
        yesterday = now - timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        # Convert to UTC for database query
        yesterday_start_utc = yesterday_start.astimezone(pytz.UTC)
        yesterday_end_utc = yesterday_end.astimezone(pytz.UTC)

        # Get messages
        query = """
            SELECT m.message_text, m.telegram_message_id, m.telegram_reply_to_message_id,
                   u.user_id, u.first_name, u.last_name, u.username
            FROM telegram_message m
            JOIN telegram_user u ON m.user_id = u.user_id
            WHERE m.chat_id = ?
            AND m.created_at BETWEEN ? AND ?
            ORDER BY m.telegram_message_id ASC
        """
        messages = await db_service.fetch_all(
            query,
            (chat_id, yesterday_start_utc.isoformat(), yesterday_end_utc.isoformat()),
        )

        return messages
    except Exception as e:
        logger.error(f"Error getting yesterday's messages: {e}", exc_info=True)
        raise


async def generate_daily_summary(chat_id: int) -> str:
    """
    Generate a daily summary for a specific chat
    """
    try:
        # Get yesterday's messages
        messages = await get_yesterdays_messages(chat_id)

        if not messages:
            return "No hay mensajes del día anterior para resumir."

        # Format messages for summary
        formatted_messages = format_recent_messages(messages)

        # Generate summary
        summary = await openai_service.get_summary(formatted_messages, "chat")

        # Add header to summary
        madrid_tz = pytz.timezone("Europe/Madrid")
        yesterday = (datetime.now(madrid_tz) - timedelta(days=1)).strftime("%d/%m/%Y")

        final_summary = f"📅 **Resumen del día {yesterday}**\n\n" f"{summary}"

        return final_summary
    except Exception as e:
        logger.error(f"Error generating daily summary: {e}", exc_info=True)
        error_msg = (
            "❌ Error al generar el resumen diario.\n"
            "Por favor, contacta con el administrador si el problema persiste."
        )
        return error_msg


async def send_daily_summaries():
    """
    Send daily summaries to all chats that have enabled the feature
    """
    try:
        # Get all chats with daily summary enabled
        query = """
            SELECT chat_id
            FROM telegram_chat_state
            WHERE daily_summary_enabled = TRUE
        """
        enabled_chats = await db_service.fetch_all(query)

        if not enabled_chats:
            logger.info("No chats have daily summaries enabled")
            return

        logger.info(f"Generating daily summaries for {len(enabled_chats)} chats")

        for chat in enabled_chats:
            chat_id = chat["chat_id"]
            try:
                summary = await generate_daily_summary(chat_id)
                # Send the summary using the message service
                await message_service.send_message(
                    chat_id=chat_id, text=summary, parse_mode="Markdown"
                )
                logger.info(f"Sent daily summary to chat {chat_id}")
            except Exception as e:
                logger.error(f"Error processing summary for chat {chat_id}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error in send_daily_summaries: {e}", exc_info=True)
