from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest, TimedOut, NetworkError, RetryAfter
from ..utils.logger import logger
from ..config import config

logger = logger.get_logger(__name__)


async def notify_admins(context: ContextTypes.DEFAULT_TYPE, message: str):
    """Notify admins about critical errors"""
    if not config.ADMIN_USERS:
        return

    for admin_id in config.ADMIN_USERS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🚨 *ALERTA DE ERROR*\n{message}",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot with detailed error categorization"""

    error = context.error
    try:
        raise error
    except BadRequest as e:
        # handle malformed requests
        error_message = f"❌ Solicitud incorrecta: {e}"
        logger.error(error_message)
        if update and hasattr(update, "effective_message"):
            await update.effective_message.reply_text(
                "Lo siento, no pude procesar tu solicitud. Por favor, inténtalo de nuevo."
            )

    except TimedOut as e:
        # handle slow connection problems
        error_message = f"⌛ Tiempo de espera agotado: {e}"
        logger.warning(error_message)
        if update and hasattr(update, "effective_message"):
            await update.effective_message.reply_text(
                "El servidor está tardando en responder. Por favor, inténtalo de nuevo en unos momentos."
            )

    except NetworkError as e:
        # handle other connection problems
        error_message = f"🌐 Error de red: {e}"
        logger.error(error_message)
        await notify_admins(context, f"Error de red detectado:\n{error_message}")

    except RetryAfter as e:
        # handle flood control
        error_message = f"⏳ Flood control: retry after {e.retry_after} seconds"
        logger.warning(error_message)
        if update and hasattr(update, "effective_message"):
            await update.effective_message.reply_text(
                f"Demasiadas solicitudes. Por favor, espera {e.retry_after} segundos."
            )

    except TelegramError as e:
        # handle all other telegram related errors
        error_message = f"📱 Error de Telegram: {e}"
        logger.error(error_message)
        await notify_admins(context, error_message)

    except Exception as e:
        # handle all other errors
        error_message = f"💥 Error crítico: {e}"
        logger.critical(error_message, exc_info=True)
        await notify_admins(context, f"Error crítico detectado:\n{error_message}")

        if update and hasattr(update, "effective_message"):
            await update.effective_message.reply_text(
                "Ha ocurrido un error inesperado. Los administradores han sido notificados."
            )

    finally:
        # Log additional information if available
        if update and hasattr(update, "effective_user"):
            user_info = (
                f"\nUsuario: {update.effective_user.id}"
                f"\nNombre: {update.effective_user.first_name}"
            )
            logger.error(user_info)

        if update and hasattr(update, "effective_chat"):
            chat_info = (
                f"\nChat: {update.effective_chat.id}"
                f"\nTipo: {update.effective_chat.type}"
            )
            logger.error(chat_info)

        if update and hasattr(update, "effective_message"):
            message_info = f"\nMensaje: {update.effective_message.text}"
            logger.error(message_info)
