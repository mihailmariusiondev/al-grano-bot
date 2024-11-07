from telegram import Message
from telegram.ext import CallbackContext
from bot.utils.media_utils import (
    transcribe_audio,
    process_media,
    compress_audio,
    get_file_size,
)
from bot.utils.constants import MAX_FILE_SIZE
import tempfile
import os
import mimetypes
import logging


async def audio_handler(message: Message, context: CallbackContext) -> None:
    # Determine the file size based on whether it's an audio or voice message
    file_size = message.audio.file_size if message.audio else message.voice.file_size

    # Check if the file size exceeds the maximum allowed size
    if file_size > MAX_FILE_SIZE:
        await message.chat.send_message(
            "El archivo es demasiado grande (más de 20 MB). Por favor, envía un archivo más pequeño."
        )
        return

    await message.chat.send_message("Procesando el audio, por favor espera...")

    # Get the file object from the message
    file = await context.bot.get_file(
        message.audio.file_id if message.audio else message.voice.file_id
    )

    # Determine the file extension based on the file path
    file_extension = mimetypes.guess_extension(file.file_path.split(".")[-1]) or ".ogg"

    # Create a temporary file to store the audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
    temp_file_path = temp_file.name
    temp_file.close()

    try:
        # Download the audio file to the temporary location
        await file.download_to_drive(custom_path=temp_file_path)
        logging.info(f"Audio downloaded. File size: {get_file_size(temp_file_path)}")

        # Compress the audio
        compressed_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=".ogg"
        ).name
        await compress_audio(temp_file_path, compressed_file_path)
        logging.info(
            f"Audio compressed. File size: {get_file_size(compressed_file_path)}"
        )

        # Transcribe the compressed audio file
        logging.info("Starting transcription...")
        transcription = await transcribe_audio(compressed_file_path)
        logging.info(f"Transcription complete. Length: {len(transcription)} characters")

        return transcription

    except Exception as e:
        # Log any errors that occur during processing
        logging.error(f"Error al transcribir el audio: {e}")
        await message.reply_text(
            "Ocurrió un error al procesar la transcripción del audio."
        )
    finally:
        # Clean up: remove both temporary files
        for file_path in [temp_file_path, compressed_file_path]:
            try:
                os.unlink(file_path)
                logging.info(f"Temporary file removed: {file_path}")
            except Exception as e:
                logging.error(f"Error al eliminar el archivo temporal: {e}")
