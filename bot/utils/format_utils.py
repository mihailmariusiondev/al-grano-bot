import logging
from typing import List, Dict
from telegram import Update
from telegram.constants import MessageLimit
from bot.utils.constants import PAUSE_BETWEEN_CHUNKS
import asyncio


def format_recent_messages(recent_messages: List[Dict]) -> str:
    """Format recent messages for summarization"""
    logging.info(f"Formatting recent messages: {recent_messages}")

    formatted_messages = []

    # Reverse messages to maintain chronological order (oldest first)
    for message in reversed(recent_messages):
        # Extract user info
        user_name = (
            message["first_name"] or message["username"] or str(message["user_id"])
        )

        # Format message with reply if exists
        if message["telegram_reply_to_message_id"]:
            formatted_message = f"{user_name} (replying to {message['telegram_reply_to_message_id']}): {message['message_text']}"
        else:
            formatted_message = f"{user_name}: {message['message_text']}"

        formatted_messages.append(formatted_message)

    result = "\n".join(formatted_messages)
    logging.info(f"Formatted recent messages: {result}")
    return result


async def send_long_message(update: Update, text: str) -> None:
    """Split and send long messages respecting Telegram's limits"""
    chunks = [
        text[i : i + MessageLimit.MAX_TEXT_LENGTH]
        for i in range(0, len(text), MessageLimit.MAX_TEXT_LENGTH)
    ]

    for chunk in chunks:
        await update.message.reply_text(chunk)
        if len(chunks) > 1:
            await asyncio.sleep(PAUSE_BETWEEN_CHUNKS)
