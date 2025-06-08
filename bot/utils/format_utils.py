import logging
from typing import List, Dict, Optional
from telegram import Update
from telegram.constants import MessageLimit
from bot.utils.constants import PAUSE_BETWEEN_CHUNKS
from bot.services.message_service import message_service
import asyncio
from datetime import datetime
import pytz


def format_recent_messages(recent_messages: List[Dict]) -> str:
    """Format recent messages for summarization with enhanced context"""
    logging.info(f"Formatting {len(recent_messages)} recent messages for summarization")

    if not recent_messages:
        return "No messages to format"

    # Create a lookup map for message IDs to resolve replies
    message_lookup = {}
    for msg in recent_messages:
        message_lookup[msg["telegram_message_id"]] = msg

    formatted_messages = []

    # Process messages in chronological order
    for message in recent_messages:
        # Extract user info with fallback
        user_name = (
            message.get("first_name") or
            message.get("username") or
            f"User{message.get('user_id', 'Unknown')}"
        )

        # Format timestamp if available
        timestamp_str = ""
        if message.get("created_at"):
            try:
                # Parse the timestamp and convert to Madrid timezone
                dt = datetime.fromisoformat(message["created_at"].replace('Z', '+00:00'))
                madrid_tz = pytz.timezone("Europe/Madrid")
                dt_madrid = dt.astimezone(madrid_tz)
                timestamp_str = f"[{dt_madrid.strftime('%H:%M')}] "
            except Exception as e:
                logging.debug(f"Error parsing timestamp {message.get('created_at')}: {e}")

        message_text = message.get("message_text", "")

        # Handle reply references
        if message.get("telegram_reply_to_message_id"):
            reply_id = message["telegram_reply_to_message_id"]

            # Try to resolve the replied message
            if reply_id in message_lookup:
                replied_msg = message_lookup[reply_id]
                replied_user = (
                    replied_msg.get("first_name") or
                    replied_msg.get("username") or
                    f"User{replied_msg.get('user_id', 'Unknown')}"
                )
                replied_text = replied_msg.get("message_text", "")

                # Truncate long replied messages for context
                if len(replied_text) > 100:
                    replied_text = replied_text[:100] + "..."

                formatted_message = (
                    f"{timestamp_str}{user_name} "
                    f"(replying to {replied_user}: \"{replied_text}\"): {message_text}"
                )
            else:
                # Fallback if we can't resolve the reply
                formatted_message = (
                    f"{timestamp_str}{user_name} "
                    f"(replying to message #{reply_id}): {message_text}"
                )
        else:
            formatted_message = f"{timestamp_str}{user_name}: {message_text}"

        formatted_messages.append(formatted_message)

    # Add conversation metadata
    total_messages = len(formatted_messages)
    unique_users = len(set(
        msg.get("first_name") or msg.get("username") or f"User{msg.get('user_id', 'Unknown')}"
        for msg in recent_messages
    ))

    # Create the formatted output with context header
    result = f"=== CONVERSATION CONTEXT ===\n"
    result += f"Total messages: {total_messages}\n"
    result += f"Participants: {unique_users}\n"
    result += f"=== MESSAGES ===\n\n"
    result += "\n".join(formatted_messages)

    logging.info(f"Formatted conversation: {len(result)} chars, {total_messages} messages, {unique_users} participants")
    return result


async def send_long_message(update: Update, text: str) -> None:
    """Split and send long messages respecting Telegram's limits

    This function maintains backward compatibility with the existing interface
    while leveraging the improved message_service functionality.
    """
    chat_id = update.effective_chat.id

    # Use the improved message_service which handles long messages automatically
    success = await message_service.send_message(chat_id, text)

    if not success:
        # Fallback to basic reply if message_service fails
        logging.warning(f"Message service failed for chat {chat_id}, using fallback")
        try:
            chunks = [
                text[i : i + MessageLimit.MAX_TEXT_LENGTH]
                for i in range(0, len(text), MessageLimit.MAX_TEXT_LENGTH)
            ]

            for chunk in chunks:
                await update.message.reply_text(chunk)
                if len(chunks) > 1:
                    await asyncio.sleep(PAUSE_BETWEEN_CHUNKS)
        except Exception as e:
            logging.error(f"Fallback also failed for chat {chat_id}: {e}")
            raise
