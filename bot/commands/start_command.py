from telegram import Update
from bot.services import db_service
from bot.utils.decorators import log_command
from bot.utils.logger import logger
from telegram.ext import ContextTypes

logger = logger.get_logger(__name__)

START_MESSAGE = "¡Eeeeeeh, figura! Bienvenido/a al puto bot de resumen de mierdas. Soy el puto amo resumiendo tus mierdas."


@log_command()
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        # Get or create user
        user = update.effective_user
        await db_service.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        await db_service.update_chat_state(chat_id, {"is_bot_started": True})
        await update.message.reply_text(START_MESSAGE, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error en start_handler: {e}")
        raise e
