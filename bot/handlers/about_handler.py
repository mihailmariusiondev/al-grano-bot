from telegram import Update
from telegram.ext import ContextTypes
from ..utils.logger import logger
from ..utils.decorators import rate_limit

logger = logger.get_logger("handlers.about")


@rate_limit(30)  # Limitar uso cada 30 segundos
async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /about command"""
    logger.info(f"About command received from user {update.effective_user.id}")

    about_text = (
        "Bot creado por @Arkantos2374 con ❤️.\n\n"
        "Este bot utiliza la API de OpenAI para procesar y responder mensajes de forma inteligente.\n\n"
        "Puedes apoyar el desarrollo del bot haciendo una donación vía "
        "[PayPal](https://paypal.me/mariusmihailion)."
    )

    await update.message.reply_text(about_text, parse_mode="Markdown")
    logger.debug(f"About response sent to user {update.effective_user.id}")
