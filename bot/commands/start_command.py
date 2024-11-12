from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from services import db_service
from utils.decorators import log_command, rate_limit_by_chat
from utils.logger import logger

logger = logger.get_logger(__name__)

START_MESSAGE = "¡Eeeeeeh, figura! Bienvenido/a al puto bot de resumen de mierdas. Soy el puto amo resumiendo tus mierdas."


@rate_limit_by_chat(30)
@log_command()
async def start_command(update: Update, context: CallbackContext):
    try:
        chat_id = update.effective_chat.id
        await db_service.update_chat_state(chat_id, {"is_bot_started": True})
        await update.message.reply_text(START_MESSAGE, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error en start_handler: {e}")
        raise e
