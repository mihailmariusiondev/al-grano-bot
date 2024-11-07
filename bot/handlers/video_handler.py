import tempfile
import os
import logging
from telegram import Message
from telegram.ext import CallbackContext
from bot.services import openai_service
from bot.utils.media_utils import compress_audio, extract_audio, get_file_size
from utils.constants import MAX_FILE_SIZE

logging = logging.getLogger(__name__)
async def video_handler(message: Message, context: CallbackContext) -> None:
    """
    Handle video message transcription requests.

    Args:
        message: Telegram message containing video
        context: Callback context
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    file_id = message.video.file_id
    file_size = message.video.file_size

    logging.info(f"Processing video from user {user_id}, file_id: {file_id}")
    logging.info(f"Video file size: {file_size} bytes")

    # Check file size limit
    if file_size > MAX_FILE_SIZE:
        logging.warning(
            f"Video size {file_size} exceeds limit of {MAX_FILE_SIZE} bytes"
        )
        await message.chat.send_message(
            "El archivo es demasiado grande (más de 20 MB). Por favor, envía un archivo más pequeño."
        )
        return

    await message.chat.send_message("Procesando el video, por favor espera...")

    # Create temporary files
    temp_file_path = None
    audio_file_path = None
    compressed_file_path = None

    try:
        # Get video file from Telegram
        file = await context.bot.get_file(file_id)
        logging.info(f"Retrieved file info: {file.file_path}")

        # Create temporary files
        temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        audio_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        compressed_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=".ogg"
        ).name

        # Download video
        await file.download_to_drive(custom_path=temp_file_path)
        logging.info(
            f"Video downloaded successfully, size: {get_file_size(temp_file_path)}"
        )

        # Extract audio from video
        await extract_audio(temp_file_path, audio_file_path)
        logging.info(f"Audio extracted, size: {get_file_size(audio_file_path)}")

        # Compress extracted audio
        await compress_audio(audio_file_path, compressed_file_path)
        logging.info(f"Audio compressed, size: {get_file_size(compressed_file_path)}")

        # Transcribe audio
        logging.info("Starting transcription process")
        transcription = await openai_service.transcribe_audio(compressed_file_path)
        logging.info(f"Transcription completed, length: {len(transcription)} chars")

        return transcription

    except Exception as e:
        logging.error(f"Error processing video: {str(e)}", exc_info=True)
        await message.reply_text(
            "Ocurrió un error al procesar la transcripción del video."
        )
        raise

    finally:
        # Cleanup temporary files
        for file_path in [temp_file_path, audio_file_path, compressed_file_path]:
            if file_path:
                try:
                    os.unlink(file_path)
                    logging.info(f"Removed temporary file: {file_path}")
                except Exception as e:
                    logging.error(
                        f"Error removing temporary file {file_path}: {str(e)}"
                    )
