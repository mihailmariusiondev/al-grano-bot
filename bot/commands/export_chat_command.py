from datetime import datetime
import json
import tempfile
import os
import pytz
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command, bot_started
from bot.services.database_service import db_service
from bot.utils.logger import logger
from bot.utils.constants import EXPORT_PROGRESS_BATCH_SIZE

# Consistent with other commands
logger = logger.get_logger(__name__)

# Error messages following the project pattern
ERROR_MESSAGES = {
    "NO_MESSAGES": "No hay mensajes para exportar hoy.",
    "EXPORT_ERROR": "❌ Error al exportar el chat.",
    "FILE_CREATION_ERROR": "❌ Error al crear el archivo de exportación.",
    "SEND_ERROR": "❌ Error al enviar el archivo."
}

SUCCESS_MESSAGES = {
    "EXPORT_SUCCESS": "✅ Chat exportado exitosamente.",
    "FILE_READY": "📄 Archivo de exportación listo."
}


@log_command()
@bot_started()
async def export_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export today's messages in a JSON file"""
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.debug(f"=== EXPORT CHAT COMMAND ===")
    logger.debug(f"Chat ID: {chat_id}, User ID: {user.id}")
    logger.debug(f"User: {user.first_name} {user.last_name} (@{user.username})")

    try:
        # Use consistent timezone handling as in other commands
        madrid_tz = pytz.timezone("Europe/Madrid")
        today = datetime.now(madrid_tz).date()

        logger.debug(f"Exporting messages for date: {today}")
        logger.debug("Fetching messages from database...")

        messages = await db_service.get_messages_for_date(chat_id, today)

        if not messages:
            logger.info(f"No messages found for export - Chat: {chat_id}, Date: {today}")
            await update.message.reply_text(ERROR_MESSAGES["NO_MESSAGES"])
            return

        logger.debug(f"Found {len(messages)} messages for export")
        logger.debug("Processing messages for JSON export...")

        entries = []
        for i, msg in enumerate(messages):
            try:
                # Consistent datetime handling
                created_utc = datetime.fromisoformat(msg["created_at"]).replace(tzinfo=pytz.UTC)
                created = created_utc.astimezone(madrid_tz)
                timestamp = created.strftime("%Y-%m-%d %H:%M")

                # Better username fallback handling
                username = (
                    msg.get("username")
                    or msg.get("first_name")
                    or str(msg.get("user_id"))
                )

                text = msg.get("message_text", "")
                reply_to = msg.get("telegram_reply_to_message_id")

                # Formatted message for readability
                formatted = (
                    f"{username} (replying to {reply_to}): {text}"
                    if reply_to
                    else f"{username}: {text}"
                )

                entries.append({
                    "timestamp": timestamp,
                    "user": username,
                    "message_id": msg.get("telegram_message_id"),
                    "reply_to_message_id": reply_to,
                    "text": text,
                    "formatted": formatted,
                })

                # Log progress for large exports
                if (i + 1) % EXPORT_PROGRESS_BATCH_SIZE == 0:
                    logger.debug(f"Processed {i + 1}/{len(messages)} messages")

            except Exception as msg_error:
                logger.warning(f"Error processing message {i}: {msg_error}")
                continue

        logger.debug(f"Successfully processed {len(entries)} messages")
        logger.debug("Creating temporary file for export...")

        # Create temporary file for export
        try:
            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json", encoding='utf-8') as tmp:
                json.dump(entries, tmp, ensure_ascii=False, indent=2)
                tmp_path = tmp.name

            logger.debug(f"Temporary file created: {tmp_path}")

        except Exception as file_error:
            logger.error(f"Error creating temporary file: {file_error}", exc_info=True)
            await update.message.reply_text(ERROR_MESSAGES["FILE_CREATION_ERROR"])
            return

        # Send the document
        try:
            logger.debug("Sending document to user...")
            with open(tmp_path, "rb") as doc:
                # Generate filename with date for clarity
                filename = f"chat_export_{today.strftime('%Y-%m-%d')}.json"
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=doc,
                    filename=filename,
                    caption=f"📄 Exportación del chat - {today.strftime('%d/%m/%Y')}"
                )

            logger.info(f"=== EXPORT CHAT COMMAND COMPLETED for user {user.id} in chat {chat_id} ===")
            logger.info(f"Exported {len(entries)} messages for date {today}")

        except Exception as send_error:
            logger.error(f"Error sending document: {send_error}", exc_info=True)
            await update.message.reply_text(ERROR_MESSAGES["SEND_ERROR"])
            return
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    logger.debug(f"Temporary file cleaned up: {tmp_path}")
            except Exception as cleanup_error:
                logger.warning(f"Error cleaning up temporary file: {cleanup_error}")

    except Exception as e:
        logger.error(f"=== EXPORT CHAT COMMAND FAILED ===")
        logger.error(f"Error in export_chat_command for user {user.id}: {e}", exc_info=True)
        try:
            await update.message.reply_text(ERROR_MESSAGES["EXPORT_ERROR"])
        except Exception as reply_error:
            logger.error(f"Failed to send error message to user: {reply_error}")
