import tempfile
import logging
import contextlib
from pathlib import Path
from telegram import Message
from telegram.ext import CallbackContext
from bot.services import openai_service
from bot.utils.media_utils import compress_audio, extract_audio, get_file_size
from bot.utils.constants import MAX_FILE_SIZE

logging = logging.getLogger(__name__)


async def video_handler(message: Message, context: CallbackContext) -> None:
    """
    Handle video and video note transcription requests.

    Args:
        message: Telegram message containing video or video note
        context: Callback context
    """
    try:
        # Get file details based on message type
        is_video_note = bool(message.video_note)
        file_id = message.video_note.file_id if is_video_note else message.video.file_id
        file_size = (
            message.video_note.file_size if is_video_note else message.video.file_size
        )

        logging.info(
            f"Processing video from user {message.from_user.id}, file_id: {file_id}"
        )
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

        # Create temporary files with context management
        temp_files = []
        with contextlib.ExitStack() as stack:
            temp_file = stack.enter_context(
                tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            )
            audio_file = stack.enter_context(
                tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            )
            compressed_file = stack.enter_context(
                tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
            )

            temp_files.extend(
                [
                    Path(temp_file.name),
                    Path(audio_file.name),
                    Path(compressed_file.name),
                ]
            )

            # Get video file from Telegram
            file = await context.bot.get_file(file_id)
            logging.info(f"Retrieved file info: {file.file_path}")

            # Download video
            await file.download_to_drive(custom_path=temp_file.name)
            logging.info(
                f"Video downloaded successfully, size: {get_file_size(temp_file.name)}"
            )

            # Extract audio from video
            await extract_audio(temp_file.name, audio_file.name)
            logging.info(f"Audio extracted, size: {get_file_size(audio_file.name)}")

            # Compress extracted audio
            await compress_audio(audio_file.name, compressed_file.name)
            logging.info(
                f"Audio compressed, size: {get_file_size(compressed_file.name)}"
            )

            # Transcribe audio
            logging.info("Starting transcription process")
            transcription = await openai_service.transcribe_audio(compressed_file.name)
            logging.info(f"Transcription completed, length: {len(transcription)} chars")

            return transcription

    except Exception as e:
        logging.error(f"Error processing video: {str(e)}", exc_info=True)
        await message.reply_text(
            "Ocurrió un error al procesar la transcripción del video."
        )
        raise

    finally:
        # Clean up temporary files
        for file_path in temp_files:
            if file_path.exists():
                with contextlib.suppress(OSError):
                    file_path.unlink()
