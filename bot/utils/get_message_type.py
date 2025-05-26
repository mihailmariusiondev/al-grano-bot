from telegram import Message
from typing import Literal

MessageType = Literal[
    "text",
    "voice",
    "audio",
    "video",
    "video_note",
    "document",
    "unknown",
]

def get_message_type(message: Message) -> MessageType:
    """
    Determina el tipo de mensaje para procesamiento de resumen.
    Orden basado en prioridad y especificidad de los tipos multimedia.
    """
    print("get_message_type function called")
    if message.voice:
        return "voice"
    elif message.audio:
        return "audio"
    elif message.video_note:
        return "video_note"
    elif message.video:
        return "video"
    elif message.document:
        return "document"
    elif message.text:
        return "text"
    return "unknown"
