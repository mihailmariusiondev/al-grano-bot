from telegram import Message
from typing import Literal

MessageType = Literal[
    "text",
    "voice",
    "audio",
    "video",
    "video_note",
    "document",
    "photo",
    "poll",
    "unknown",
]


def get_message_type(message: Message) -> MessageType:
    """
    Determina el tipo de mensaje para procesamiento de resumen.
    Orden basado en prioridad y especificidad de los tipos multimedia.
    """
    print("get_message_type function called")

    # Mensajes de audio/voz (prioridad alta por ser específicos)
    if message.voice:
        return "voice"
    elif message.audio:
        return "audio"

    # Videos (siguiente en especificidad)
    elif message.video_note:
        return "video_note"
    elif message.video:
        return "video"

    # Documentos (pueden contener varios tipos de archivos)
    elif message.document:
        return "document"

    # Contenido básico
    elif message.text:
        return "text"
    elif message.photo:
        return "photo"
    elif message.poll:
        return "poll"

    # Si no es ninguno de los tipos soportados
    return "unknown"
