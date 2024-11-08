from telegram import Message
from telegram.ext import CallbackContext
from bot.services import openai_service
from utils.constants import MAX_FILE_SIZE
from utils.media_utils import compress_audio, get_file_size
import tempfile
import os
import logging


async def audio_handler(message: Message, context: CallbackContext) -> None:
    """
    Handle audio and voice message transcription requests.

    Args:
        message: Telegram message containing audio/voice
        context: Callback context
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Determine file details based on message type
    is_audio = bool(message.audio)
    file_id = message.audio.file_id if is_audio else message.voice.file_id
    file_size = message.audio.file_size if is_audio else message.voice.file_size

    logging.info(
        f"Processing {'audio' if is_audio else 'voice'} message from user {user_id}, file_id: {file_id}"
    )
    logging.info(f"File size: {file_size} bytes")

    # Check file size limit
    if file_size > MAX_FILE_SIZE:
        logging.warning(f"File size {file_size} exceeds limit of {MAX_FILE_SIZE} bytes")
        await message.chat.send_message(
            "El archivo es demasiado grande (más de 20 MB) para resumir."
        )
        return

    try:
        # Get file from Telegram
        file = await context.bot.get_file(file_id)
        logging.info(f"Retrieved file info: {file.file_path}")

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
        temp_file_path = temp_file.name
        temp_file.close()
        logging.info(f"Created temporary file: {temp_file_path}")

        try:
            # Download audio file
            await file.download_to_drive(custom_path=temp_file_path)
            logging.info(
                f"Audio downloaded successfully, size: {get_file_size(temp_file_path)}"
            )

            # Compress audio
            compressed_file_path = tempfile.NamedTemporaryFile(
                delete=False, suffix=".ogg"
            ).name
            await compress_audio(temp_file_path, compressed_file_path)
            logging.info(
                f"Audio compressed, new size: {get_file_size(compressed_file_path)}"
            )

            # Transcribe audio
            logging.info("Starting transcription process")
            transcription = await openai_service.transcribe_audio(compressed_file_path)
            logging.info(f"Transcription completed, length: {len(transcription)} chars")

            return transcription

        except Exception as e:
            logging.error(f"Error processing audio file: {str(e)}", exc_info=True)
            await message.reply_text(
                "Ocurrió un error al procesar la transcripción del audio."
            )
            raise

        finally:
            # Cleanup temporary files
            for file_path in [temp_file_path, compressed_file_path]:
                try:
                    os.unlink(file_path)
                    logging.info(f"Removed temporary file: {file_path}")
                except Exception as e:
                    logging.error(
                        f"Error removing temporary file {file_path}: {str(e)}"
                    )

    except Exception as e:
        logging.error(f"Error in audio handler: {str(e)}", exc_info=True)
        raise
