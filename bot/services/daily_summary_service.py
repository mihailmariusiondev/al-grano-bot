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

        # Get chat state to determine summary type
        chat_state = await db_service.get_chat_state(chat_id)
        summary_type = (
            "chat_long"
            if chat_state.get("summary_type", "long") == "long"
            else "chat_short"
        )

        # Generate summary
        summary = await openai_service.get_summary(
            content=formatted_messages, summary_type=summary_type, language="Spanish"
        )

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


async def send_daily_summary_for(chat_id: int):
    """Generate and send a daily summary for a specific chat.

    Args:
        chat_id: The chat ID to summarize
    """
    try:
        logger.info(f"Generating daily summary for chat {chat_id}")

        # Get chat configuration
        config = await db_service.get_chat_summary_config(chat_id)

        # Get recent messages (last 24 hours)
        messages = await db_service.get_recent_messages_by_time(chat_id, hours=24)

        # Check if there are enough messages to summarize
        if len(messages) < 5:
            logger.info(f"Not enough messages ({len(messages)}) for chat {chat_id}, skipping summary")
            return

        # Format messages for the AI
        formatted_content = format_recent_messages(messages)

        # Determine summary type based on configuration
        summary_type = f"chat_{config['length']}"  # chat_short, chat_medium, chat_long

        # Generate summary using custom configuration
        summary = await openai_service.get_summary(
            content=formatted_content,
            summary_type=summary_type,
            language=config['language'],
            tone=config['tone'],
            include_names=config['include_names']
        )

        # Add header to summary
        madrid_tz = pytz.timezone("Europe/Madrid")
        yesterday = (datetime.now(madrid_tz) - timedelta(days=1)).strftime("%d/%m/%Y")

        final_summary = f"📅 **Resumen del día {yesterday}**\n\n{summary}"

        # Send the summary to the chat
        success = await message_service.send_message(
            chat_id=chat_id,
            text=final_summary,
            parse_mode="Markdown"
        )

        if success:
            logger.info(f"Successfully sent daily summary to chat {chat_id}")
        else:
            logger.warning(f"Failed to send daily summary to chat {chat_id}, removing scheduled job")
            try:
                from bot.services.scheduler_service import scheduler_service
                scheduler_service.remove_daily_summary_job(chat_id)
            except Exception as cleanup_error:
                logger.error(f"Error removing job for failed chat {chat_id}: {cleanup_error}")

    except Exception as e:
        logger.error(f"Error sending daily summary for chat {chat_id}: {e}", exc_info=True)


async def send_daily_summaries():
    """
    Send daily summaries to all chats that have enabled the feature
    (Backward compatibility function - now uses new configuration system)
    """
    try:
        # Get all chats with daily summary enabled using new configuration
        configs = await db_service.get_all_daily_summary_configs()

        if not configs:
            logger.info("No chats have daily summaries enabled")
            return

        logger.info(f"Generating daily summaries for {len(configs)} chats")

        for config in configs:
            chat_id = config["chat_id"]
            try:
                await send_daily_summary_for(chat_id)
            except Exception as e:
                logger.error(f"Error processing summary for chat {chat_id}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error in send_daily_summaries: {e}", exc_info=True)
