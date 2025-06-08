import tempfile
import contextlib
from pathlib import Path
from telegram import Message
from telegram.ext import CallbackContext
from bot.services import openai_service
from bot.utils.media_utils import compress_audio, extract_audio, get_file_size
from bot.utils.constants import MAX_FILE_SIZE
from bot.utils.logger import logger

logger = logger.get_logger(__name__)


async def video_handler(message: Message, context: CallbackContext) -> None:
    """
    Handle video and video note transcription requests.

    Args:
        message: Telegram message containing video or video note
        context: Callback context
    """
    logger.debug(f"=== VIDEO HANDLER STARTED ===")

    try:
        # Get file details based on message type
        is_video_note = bool(message.video_note)
        file_id = message.video_note.file_id if is_video_note else message.video.file_id
        file_size = (
            message.video_note.file_size if is_video_note else message.video.file_size
        )

        user_id = message.from_user.id
        video_type = "video_note" if is_video_note else "video"

        logger.debug(f"User ID: {user_id}")
        logger.debug(f"Video type: {video_type}")
        logger.debug(f"File ID: {file_id}")
        logger.debug(f"File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")

        logger.info(f"Processing {video_type} from user {user_id}")

        # Check file size limit
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"Video size {file_size} exceeds limit of {MAX_FILE_SIZE} bytes")
            await message.reply_text(
                "El archivo es demasiado grande (más de 20 MB). Por favor, envía un archivo más pequeño."
            )
            return None

        await message.reply_text("Procesando el video, por favor espera...")

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
            try:
                file = await context.bot.get_file(file_id)
                logging.info(f"Retrieved file info: {file.file_path}")
                await file.download_to_drive(custom_path=temp_file.name)
                logging.info(
                    f"Video downloaded successfully, size: {get_file_size(temp_file.name)}"
                )
            except Exception as e:
                logging.error(f"Error downloading video: {str(e)}", exc_info=True)
                await message.reply_text(
                    "Hubo un problema al descargar el video. Por favor, inténtalo de nuevo."
                )
                return None

            try:
                # Extract and process audio
                await extract_audio(temp_file.name, audio_file.name)
                logging.info(f"Audio extracted, size: {get_file_size(audio_file.name)}")
                await compress_audio(audio_file.name, compressed_file.name)
                logging.info(
                    f"Audio compressed, size: {get_file_size(compressed_file.name)}"
                )
            except Exception as e:
                logging.error(
                    f"Error processing audio from video: {str(e)}", exc_info=True
                )
                await message.reply_text(
                    "Hubo un problema al procesar el audio del video. Por favor, inténtalo de nuevo."
                )
                return None

            try:
                # Transcribe audio
                logging.info("Starting transcription process")
                transcription = await openai_service.transcribe_audio(
                    compressed_file.name
                )
                logging.info(
                    f"Transcription completed, length: {len(transcription)} chars"
                )
                return transcription
            except Exception as e:
                logging.error(f"Error transcribing audio: {str(e)}", exc_info=True)
                await message.reply_text(
                    "No pude transcribir el audio del video. Por favor, inténtalo de nuevo."
                )
                return None

    except Exception as e:
        logging.error(f"Error in video handler: {str(e)}", exc_info=True)
        await message.reply_text(
            "Ocurrió un error inesperado al procesar el video. Por favor, inténtalo de nuevo."
        )
        return None

    finally:
        # Clean up temporary files
        for file_path in temp_files:
            if file_path.exists():
                with contextlib.suppress(OSError):
                    file_path.unlink()
