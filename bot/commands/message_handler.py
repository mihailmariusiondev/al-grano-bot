from telegram import Update
from telegram.ext import ContextTypes

from bot.utils import get_message_type
from bot.utils.logger import logger
from bot.services.database_service import db_service

logger = logger.get_logger(__name__)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        logger.debug("No message in update, skipping")
        return

    chat_id = message.chat_id
    user = message.from_user
    message_id = message.message_id
    message_text = message.text or message.caption or ""
    reply_to_message_id = (
        message.reply_to_message.message_id if message.reply_to_message else None
    )

    logger.debug(f"=== MESSAGE HANDLER STARTED ===")
    logger.debug(f"Chat ID: {chat_id}, Message ID: {message_id}")
    logger.debug(f"User ID: {user.id if user else 'None'}, Username: {user.username if user else 'None'}")
    logger.debug(f"Message text length: {len(message_text)}")
    logger.debug(f"Reply to message ID: {reply_to_message_id}")

    message_type = get_message_type(message)
    logger.info(f"Message type: {message_type}")

    if not message_text or not user:
        logger.debug(f"Skipping message processing - Empty message: {not message_text}, No user: {not user}")
        return

    logger.info(
        f"Processing message - Chat: {chat_id}, Message ID: {message_id}, "
        f"From: {user.id} ({user.first_name}), Length: {len(message_text)} chars"
    )

    if len(message_text) > 100:
        logger.debug(f"Message preview: {message_text[:100]}...")
    else:
        logger.debug(f"Full message: {message_text}")

    try:
        # Get or create the user
        logger.debug("Getting or creating user in database...")
        saved_user = await db_service.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        logger.debug(f"User processed: {saved_user['user_id']}")

        # Get chat state
        logger.debug("Getting chat state...")
        chat_state = await db_service.get_chat_state(chat_id)
        logger.debug(f"Chat state retrieved for: {chat_state['chat_id']}")

        # Save the message details to the database
        logger.debug("Saving message to database...")
        await db_service.save_message(
            chat_id=chat_id,
            user_id=saved_user["user_id"],
            message_text=message_text,
            telegram_message_id=message_id,
            telegram_reply_to_message_id=reply_to_message_id,
            message_type=message_type,
        )

        logger.info(
            f"=== MESSAGE HANDLER COMPLETED ===\n"
            f"Saved message - Sender: {saved_user['user_id']}, "
            f"Text length: {len(message_text)}, Reply to: {reply_to_message_id}, "
            f"Chat: {chat_state['chat_id']}"
        )

    except Exception as e:
        logger.error(f"=== MESSAGE HANDLER FAILED ===")
        logger.error(f"Error processing message {message_id} in chat {chat_id}: {e}", exc_info=True)
