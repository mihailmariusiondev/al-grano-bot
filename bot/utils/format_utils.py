import logging
from typing import List, Dict


def format_recent_messages(recent_messages: List[Dict]) -> str:
    logging.info(f"Formatting recent messages: {recent_messages}")

    formatted_messages = []
    for message in recent_messages:
        user = message["user"]
        message_content = message["message"]

        if message_content.get("telegramReplyToMessageId"):
            formatted_message = f"{user['firstName']} (replying to {message_content['telegramReplyToMessageId']})"
        else:
            formatted_message = f"{user['firstName']}: {message_content['messageText']}"

        formatted_messages.append(formatted_message)

    result = " | ".join(formatted_messages)

    logging.info(f"Formatted recent messages: {result}")

    return result
