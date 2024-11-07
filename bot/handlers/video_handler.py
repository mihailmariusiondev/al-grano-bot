import tempfile
import os
import logging
from telegram import Message
from telegram.ext import CallbackContext
from ..utils.media_utils import (
    compress_audio,
    extract_audio,
    get_file_size,
)
from ..services.openai_service import openai_service
from ..utils.constants import MAX_FILE_SIZE


async def video_handler(message: Message, context: CallbackContext) -> None:
    # Check if the video file size exceeds the maximum allowed size
    if message.video.file_size > MAX_FILE_SIZE:
        await message.chat.send_message(
            "El archivo es demasiado grande (más de 20 MB). Por favor, envía un archivo más pequeño."
        )
        return

    await message.chat.send_message("Procesando el video, por favor espera...")

    # Get the video file from the message
    file = await context.bot.get_file(message.video.file_id)

    # Create a temporary file to store the video
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file_path = temp_file.name
    temp_file.close()

    try:
        # Download the video file to the temporary location
        await file.download_to_drive(custom_path=temp_file_path)
        logging.info(f"Video downloaded. File size: {get_file_size(temp_file_path)}")

        # Extract audio from video
        audio_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        await extract_audio(temp_file_path, audio_file_path)
        logging.info(f"Audio extracted. File size: {get_file_size(audio_file_path)}")

        # Compress the extracted audio
        compressed_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=".ogg"
        ).name
        await compress_audio(audio_file_path, compressed_file_path)
        logging.info(
            f"Audio compressed. File size: {get_file_size(compressed_file_path)}"
        )

        # Transcribe the compressed audio file
        logging.info("Starting transcription...")
        try:
            transcription = await openai_service.transcribe_audio(compressed_file_path)
            logging.info(f"Transcription complete. Length: {len(transcription)} characters")
            return transcription
        except RuntimeError as e:
            logging.error(f"Transcription failed: {e}")
            await message.reply_text(
                "Ocurrió un error al transcribir el audio del video."
            )
            return None

    except Exception as e:
        # Log any errors that occur during processing
        logging.error(f"Error al transcribir el video: {e}")
        await message.reply_text(
            "Ocurrió un error al procesar la transcripción del video."
        )
    finally:
        # Clean up: remove all temporary files
        for file_path in [temp_file_path, audio_file_path, compressed_file_path]:
            try:
                os.unlink(file_path)
                logging.info(f"Temporary file removed: {file_path}")
            except Exception as e:
                logging.error(f"Error al eliminar el archivo temporal: {e}")
