from telegram import Update
from telegram.ext import ContextTypes
from ..utils.logger import logger
from ..config import config

logger = logger.get_logger("handlers.help")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    is_admin = update.effective_user.id in (config.ADMIN_USERS or [])

    help_text = (
        "Este bot utiliza IA para conversar contigo.\n\n"
        "Comandos disponibles:\n"
        "/start - Iniciar el bot\n"
        "/help - Mostrar este mensaje de ayuda\n"
        "/about - Información sobre el bot\n"
    )

    if is_admin:
        help_text += (
            "\nComandos de administrador:\n"
            "/stats - Ver estadísticas del bot\n"
            "/broadcast - Enviar mensaje a todos los usuarios"
        )

    await update.message.reply_text(help_text)
    logger.debug(f"Help response sent to user {update.effective_user.id}")
