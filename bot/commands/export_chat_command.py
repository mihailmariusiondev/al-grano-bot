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

log = logger.get_logger(__name__)


@log_command()
@bot_started()
async def export_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export today's messages in a JSON file"""
    try:
        chat_id = update.effective_chat.id
        madrid_tz = pytz.timezone("Europe/Madrid")
        today = datetime.now(madrid_tz).date()

        messages = await db_service.get_messages_for_date(chat_id, today)
        if not messages:
            await update.message.reply_text("No hay mensajes para exportar hoy.")
            return

        entries = []
        for msg in messages:
            created = datetime.fromisoformat(msg["created_at"]).astimezone(madrid_tz)
            timestamp = created.strftime("%Y-%m-%d %H:%M")
            username = (
                msg.get("username")
                or msg.get("first_name")
                or str(msg.get("user_id"))
            )
            text = msg.get("message_text", "")
            reply_to = msg.get("telegram_reply_to_message_id")
            formatted = (
                f"{username} (replying to {reply_to}): {text}"
                if reply_to
                else f"{username}: {text}"
            )
            entries.append(
                {
                    "timestamp": timestamp,
                    "user": username,
                    "message_id": msg.get("telegram_message_id"),
                    "reply_to_message_id": reply_to,
                    "text": text,
                    "formatted": formatted,
                }
            )

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            json.dump(entries, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as doc:
            await context.bot.send_document(
                chat_id=chat_id,
                document=doc,
                filename="chat_export.json",
            )

        os.remove(tmp_path)
    except Exception as e:
        log.error(f"Error in export_chat_command: {e}", exc_info=True)
        await update.message.reply_text("❌ Error al exportar el chat.")
        raise
