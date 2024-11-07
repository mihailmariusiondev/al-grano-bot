from telegram import Update
from telegram.ext import ContextTypes
from ..utils.logger import logger
from ..services import db_service
from ..utils.decorators import rate_limit

logger = logger.get_logger(__name__)


@rate_limit(60)  # Evitar spam del comando start
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id
    username = update.effective_user.username

    try:
        await db_service.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username),
        )

        start_text = (
            "¡Hola! Me has iniciado. Puedes enviarme mensajes y te responderé usando IA."
        )
        await update.message.reply_text(start_text)
        logger.debug(f"Start response sent to user {user_id}")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        raise
