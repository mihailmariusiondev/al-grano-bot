import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils import get_message_type
from ..utils.logger import logger
from ..services.database_service import db_service
from utils.constants import CLEANUP_THRESHOLDS

logger = logger.get_logger(__name__)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    chat_id = message.chat_id
    user = message.from_user
    message_id = message.message_id
    message_text = message.text or message.caption or ""
    reply_to_message_id = message.reply_to_message.message_id if message.reply_to_message else None
    message_type = get_message_type(message)

    logger.info(f"Message type: {message_type}")

    if not message_text or not user:
        return

    logging.info(
        f"Received message details - Chat ID: {chat_id}, Message ID: {message_id}, "
        f"From ID: {user.id}, First Name: {user.first_name}, Text: {message_text}"
    )

    # Get or create the user
    saved_user = await db_service.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    # Get or create the chat config
    chat_config = await db_service.get_chat_config(chat_id)

    # Save the message details to the database
    await db_service.save_message(
        chat_id=chat_id,
        user_id=saved_user['user_id'],
        message_text=message_text,
        telegram_message_id=message_id,
        telegram_reply_to_message_id=reply_to_message_id,
        message_type=message_type
    )

    logging.info(
        f"Saved message details - Sender: {saved_user['user_id']}, Text: {message_text}, "
        f"ReplyTo: {reply_to_message_id}, ChatConfig: {chat_config['chat_id']}"
    )

    # Check message count and cleanup if needed
    message_count = await db_service.get_message_count(chat_id)
    if message_count > CLEANUP_THRESHOLDS['CLEANUP_THRESHOLD']:
        logger.info(f"Chat {chat_id} reached message threshold, cleaning up old messages")
        await db_service.cleanup_old_messages(
            chat_id,
            days=CLEANUP_THRESHOLDS['DAYS_TO_KEEP'],
            keep_minimum=CLEANUP_THRESHOLDS['MINIMUM_MESSAGES']
        )

    await update.message.reply_text("Recibí tu mensaje de texto.")
