from telegram import Update
from bot.services import db_service
from bot.utils.decorators import log_command
from bot.utils.logger import logger
from telegram.ext import ContextTypes

logger = logger.get_logger(__name__)

START_MESSAGE = (
    "¡Hola! Bienvenido/a al bot de resúmenes. Soy tu asistente para resumir contenido.\n\n"
    "Puedo resumir conversaciones, artículos, videos de YouTube, audios y más. "
    "Simplemente usa /summarize o responde a un mensaje con /summarize.\n\n"
    "Para personalizar los resúmenes (tono, idioma, etc.), usa /configurar_resumen.\n\n"
    "Escribe /help para ver todos los comandos disponibles."
)


@log_command()
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        user = update.effective_user

        # Get or create user
        await db_service.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        # Update chat state
        await db_service.update_chat_state(chat_id, {"is_bot_started": True})

        # Send welcome message
        await update.message.reply_text(START_MESSAGE)

    except Exception as e:
        logger.error(f"Error en start_command: {e}", exc_info=True)
        try:
            await update.message.reply_text("Error al inicializar el bot. Por favor, inténtalo de nuevo.")
        except:
            pass
