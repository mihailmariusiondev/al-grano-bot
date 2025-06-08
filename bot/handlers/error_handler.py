from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest, TimedOut, NetworkError, RetryAfter
from ..utils.logger import logger
from ..services import db_service
import traceback
import sys

logger = logger.get_logger(__name__)

async def notify_admins(context: ContextTypes.DEFAULT_TYPE, message: str):
    """Notify all admin users about an error."""
    admin_users = await db_service.get_admin_users()
    for admin_id in admin_users:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot with detailed error categorization"""

    # Get current system exception
    exc_info = sys.exc_info()

    # Extract basic info for logging
    error_type = type(context.error).__name__
    error_message = str(context.error)
    user_id = getattr(update, 'effective_user', {}).id if hasattr(update, 'effective_user') and update.effective_user else 'Unknown'
    chat_id = getattr(update, 'effective_chat', {}).id if hasattr(update, 'effective_chat') and update.effective_chat else 'Unknown'

    logger.error(f"=== ERROR HANDLER TRIGGERED ===")
    logger.error(f"Error Type: {error_type}")
    logger.error(f"Error Message: {error_message}")
    logger.error(f"User ID: {user_id}, Chat ID: {chat_id}")

    # Log complete error information
    logger.error(
        "\n=== Detailed Error Information ===\n"
        f"Error Type: {error_type}\n"
        f"Error Message: {error_message}\n"
        f"Update: {update}\n"
        f"Chat Data: {context.chat_data}\n"
        f"User Data: {context.user_data}\n"
        f"=== Full Traceback ===\n"
        f"{''.join(traceback.format_tb(exc_info[2]))}\n"
        "=========================================="
    )

    error = context.error
    try:
        raise error
    except BadRequest as e:
        error_message = f"❌ Solicitud incorrecta: {e}"
        logger.error(f"BadRequest Error:\n"
                    f"Error: {str(e)}\n"
                    f"Update: {update}\n"
                    f"Context: {context}")
        if update and hasattr(update, "effective_message"):
            await update.effective_message.reply_text(
                "Lo siento, no pude procesar tu solicitud. Por favor, inténtalo de nuevo."
            )

    except TimedOut as e:
        error_message = f"⌛ Tiempo de espera agotado: {e}"
        logger.warning(f"Timeout Error:\n"
                      f"Error: {str(e)}\n"
                      f"Update: {update}\n"
                      f"Context: {context}")
        if update and hasattr(update, "effective_message"):
            await update.effective_message.reply_text(
                "El servidor está tardando en responder. Por favor, inténtalo de nuevo en unos momentos."
            )

    except NetworkError as e:
        error_message = f"🌐 Error de red: {e}"
        logger.error(f"Network Error:\n"
                    f"Error: {str(e)}\n"
                    f"Update: {update}\n"
                    f"Context: {context}")
        await notify_admins(context, f"Error de red detectado:\n{error_message}")

    except Exception as e:
        # Log detailed error information
        logger.critical(
            "\n=== Critical Error ===\n"
            f"Error Type: {type(e).__name__}\n"
            f"Error Message: {str(e)}\n"
            f"Update: {update}\n"
            f"Chat Data: {context.chat_data}\n"
            f"User Data: {context.user_data}\n"
            f"=== Stack Trace ===\n"
            f"{''.join(traceback.format_tb(exc_info[2]))}\n"
            "===================="
        )

        if update and hasattr(update, "effective_message"):
            await update.effective_message.reply_text(
                "Ha ocurrido un error al procesar tu solicitud. Por favor, inténtalo de nuevo."
            )

    finally:
        # Log detailed context information
        context_info = {
            "update": update,
            "error": context.error,
            "chat_data": context.chat_data,
            "user_data": context.user_data,
            "bot_data": context.bot_data
        }

        logger.info("\n=== Context Information ===")
        for key, value in context_info.items():
            logger.info(f"{key}: {value}")

        # Log user information if available
        if update and hasattr(update, "effective_user"):
            user = update.effective_user
            logger.info(
                "\n=== User Information ===\n"
                f"User ID: {user.id}\n"
                f"Username: {user.username}\n"
                f"First Name: {user.first_name}\n"
                f"Last Name: {user.last_name}\n"
                f"Language Code: {user.language_code}"
            )

        # Log chat information if available
        if update and hasattr(update, "effective_chat"):
            chat = update.effective_chat
            logger.info(
                "\n=== Chat Information ===\n"
                f"Chat ID: {chat.id}\n"
                f"Chat Type: {chat.type}\n"
                f"Chat Title: {chat.title}"
            )

        # Log message information if available
        if update and hasattr(update, "effective_message"):
            message = update.effective_message
            logger.info(
                "\n=== Message Information ===\n"
                f"Message ID: {message.message_id}\n"
                f"Date: {message.date}\n"
                f"Text: {message.text}\n"
                f"Caption: {message.caption}"
            )

        # Notify admins with detailed error information
        error_report = (
            f"Error Type: {type(context.error).__name__}\n"
            f"Error Message: {str(context.error)}\n"
            f"Update: {update}"
        )
        await notify_admins(context, error_report)
