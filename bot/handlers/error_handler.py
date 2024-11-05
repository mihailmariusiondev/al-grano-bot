import traceback
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.logger import logger

logger = logger.get_logger("handlers.error")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot"""

    # Log the error
    logger.error("Exception while handling an update:", exc_info=context.error)

    # Extract error details
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Log update details
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    logger.error(
        f"Exception while handling an update:\n"
        f"update = {update_str}\n\n"
        f"context.chat_data = {str(context.chat_data)}\n\n"
        f"context.user_data = {str(context.user_data)}\n\n"
        f"{tb_string}"
    )

    # Notify user
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Lo siento, ha ocurrido un error al procesar tu solicitud.\n"
                "El error ha sido registrado y será revisado por el equipo de desarrollo."
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")
