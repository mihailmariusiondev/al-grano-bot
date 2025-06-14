from telegram import Message
from telegram.ext import CallbackContext
from bot.services import openai_service
from bot.utils.constants import MAX_FILE_SIZE
from bot.utils.media_utils import compress_audio, get_file_size
from bot.utils.logger import logger
from contextlib import ExitStack
import tempfile
import os  # Necesario para os.path.getsize

logger = logger.get_logger(__name__)


async def audio_handler(message: Message, context: CallbackContext) -> None:
    """
    Handle audio and voice message transcription requests.

    Args:
        message: Telegram message containing audio/voice
        context: Callback context
    """
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        is_audio = bool(message.audio)
        file_id = message.audio.file_id if is_audio else message.voice.file_id
        file_size = message.audio.file_size if is_audio else message.voice.file_size

        logger.debug(f"=== AUDIO HANDLER STARTED ===")
        logger.debug(f"Chat ID: {chat_id}, User ID: {user_id}")
        logger.debug(f"Message type: {'audio' if is_audio else 'voice'}")
        logger.debug(f"File ID: {file_id}")
        logger.debug(f"File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")

        logger.info(f"Processing {'audio' if is_audio else 'voice'} message from user {user_id}")

        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File size {file_size} exceeds limit of {MAX_FILE_SIZE} bytes")
            await message.reply_text(
                "El archivo es demasiado grande (más de 20 MB). Por favor, envía un archivo más pequeño."
            )
            return None

        try:
            logger.debug("Retrieving file from Telegram")
            file = await context.bot.get_file(file_id)
            logger.info(f"Retrieved file info: {file.file_path}")

            with ExitStack() as stack:
                temp_file = stack.enter_context(
                    tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
                )
                compressed_file = stack.enter_context(
                    tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
                )
                temp_file_path = temp_file.name
                compressed_file_path = compressed_file.name

                logger.debug(f"Created temporary files: {temp_file_path}, {compressed_file_path}")

                try:
                    logger.debug("Starting file download")
                    await file.download_to_drive(custom_path=temp_file_path)

                    # --- FIX START ---
                    downloaded_size_bytes = os.path.getsize(temp_file_path)
                    logger.info(f"Audio downloaded successfully, size: {get_file_size(temp_file_path)}")

                    logger.debug("Starting audio compression")
                    await compress_audio(temp_file_path, compressed_file_path)

                    compressed_size_bytes = os.path.getsize(compressed_file_path)
                    logger.info(f"Audio compressed, new size: {get_file_size(compressed_file_path)}")

                    if downloaded_size_bytes > 0:
                        compression_ratio = compressed_size_bytes / downloaded_size_bytes
                        logger.info(f"Compression ratio: {compression_ratio:.2f}")
                    # --- FIX END ---

                    logger.debug("Starting audio transcription")
                    transcription = await openai_service.transcribe_audio(compressed_file_path)
                    transcription_length = len(transcription)
                    logger.info(f"=== AUDIO HANDLER COMPLETED SUCCESSFULLY ===")
                    logger.info(f"Transcription length: {transcription_length} chars")
                    logger.debug(f"Transcription preview: {transcription[:200]}...")

                    return transcription

                except Exception as e:
                    logger.error(f"Error processing audio file: {str(e)}", exc_info=True)
                    await message.reply_text(
                        "Ocurrió un error al procesar el audio. Por favor, inténtalo de nuevo."
                    )
                    return None

        except Exception as e:
            logger.error(f"Error getting file from Telegram: {str(e)}", exc_info=True)
            await message.reply_text(
                "No pude acceder al archivo de audio. Por favor, inténtalo de nuevo."
            )
            return None

    except Exception as e:
        logger.error(f"=== AUDIO HANDLER FAILED ===")
        logger.error(f"Unexpected error in audio handler: {str(e)}", exc_info=True)
        await message.reply_text(
            "Ocurrió un error inesperado. Por favor, inténtalo de nuevo."
        )
        return None
