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
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.debug(f"=== START COMMAND ===")
    logger.debug(f"Chat ID: {chat_id}, User ID: {user.id}")
    logger.debug(f"User: {user.first_name} {user.last_name} (@{user.username})")

    try:
        logger.debug("Getting or creating user in database...")
        # Get or create user
        saved_user = await db_service.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        logger.debug(f"User processed: {saved_user['user_id']}")

        logger.debug("Updating chat state...")
        # Update chat state
        await db_service.update_chat_state(chat_id, {"is_bot_started": True})
        logger.debug("Chat state updated: is_bot_started = True")

        logger.debug("Sending welcome message...")
        # Send welcome message
        await update.message.reply_text(START_MESSAGE)

        logger.info(f"=== START COMMAND COMPLETED for user {user.id} in chat {chat_id} ===")

    except Exception as e:
        logger.error(f"=== START COMMAND FAILED ===")
        logger.error(f"Error en start_command for user {user.id}: {e}", exc_info=True)
        try:
            await update.message.reply_text("Error al inicializar el bot. Por favor, inténtalo de nuevo.")
        except:
            logger.error("Failed to send error message to user")
