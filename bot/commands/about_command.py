from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.logger import logger
from bot.utils.decorators import log_command, bot_started

ABOUT_MESSAGE = (
    "Bot creado por @Arkantos2374 con ❤️.\n\n"
    "Puedes apoyar el desarrollo del bot haciendo una donación vía "
    "[PayPal](https://paypal.me/mariusmihailion)."
)

logger = logger.get_logger(__name__)


@log_command()
@bot_started()
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(ABOUT_MESSAGE, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error en about_handler: {e}")
        raise e
