import logging
from telegram import Message
from telegram.ext import CallbackContext
from utils.constants import (
    SUPPORTED_AUDIO_TYPES,
    SUPPORTED_VIDEO_TYPES,
    SUPPORTED_DOCUMENT_TYPES,
)
from handlers.audio_handler import audio_handler
from handlers.video_handler import video_handler


async def document_handler(message: Message, context: CallbackContext) -> None:
    """Handle document processing requests."""
    try:
        document = message.document
        mime_type = document.mime_type

        if mime_type in SUPPORTED_AUDIO_TYPES:
            return await audio_handler(message, context)
        elif mime_type in SUPPORTED_VIDEO_TYPES:
            return await video_handler(message, context)
        elif mime_type in SUPPORTED_DOCUMENT_TYPES:
            # TODO: Implement text/PDF processing
            raise NotImplementedError("Text document processing not implemented yet")
        else:
            raise ValueError(f"Unsupported document type: {mime_type}")

    except Exception as e:
        logging.error(f"Error in document handler: {str(e)}", exc_info=True)
        raise
