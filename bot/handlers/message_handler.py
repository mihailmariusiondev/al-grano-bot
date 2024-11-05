from telegram import Update
from telegram.ext import ContextTypes
from ..utils.logger import logger
from ..utils.decorators import log_command, rate_limit

logger = logger.get_logger("handlers.message")


@log_command
@rate_limit(2)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Respond to any text message received
    await update.message.reply_text("Recibí tu mensaje de texto.")
