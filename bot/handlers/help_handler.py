from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.logger import logger
from bot.utils.replies import BotReply
from bot.utils.decorators import rate_limit, log_command, bot_started

logger = logger.get_logger(__name__)

@rate_limit(30)
@log_command()
@bot_started()
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(BotReply.START_MESSAGE, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in help_handler: {e}")
        raise e
