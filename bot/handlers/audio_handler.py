from telegram import Message
from telegram.ext import CallbackContext
from bot.services import openai_service
from bot.utils.constants import MAX_FILE_SIZE
from bot.utils.media_utils import compress_audio, get_file_size
from contextlib import ExitStack
import tempfile
import logging


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

        logging.info(
            f"Processing {'audio' if is_audio else 'voice'} message from user {user_id}, file_id: {file_id}"
        )
        logging.info(f"File size: {file_size} bytes")

        if file_size > MAX_FILE_SIZE:
            logging.warning(
                f"File size {file_size} exceeds limit of {MAX_FILE_SIZE} bytes"
            )
            await message.reply_text(
                "El archivo es demasiado grande (más de 20 MB). Por favor, envía un archivo más pequeño."
            )
            return None

        try:
            file = await context.bot.get_file(file_id)
            logging.info(f"Retrieved file info: {file.file_path}")

            with ExitStack() as stack:
                temp_file = stack.enter_context(
                    tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
                )
                compressed_file = stack.enter_context(
                    tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
                )
                temp_file_path = temp_file.name
                compressed_file_path = compressed_file.name

                logging.info(
                    f"Created temporary files: {temp_file_path}, {compressed_file_path}"
                )

                try:
                    await file.download_to_drive(custom_path=temp_file_path)
                    logging.info(
                        f"Audio downloaded successfully, size: {get_file_size(temp_file_path)}"
                    )

                    await compress_audio(temp_file_path, compressed_file_path)
                    logging.info(
                        f"Audio compressed, new size: {get_file_size(compressed_file_path)}"
                    )

                    transcription = await openai_service.transcribe_audio(
                        compressed_file_path
                    )
                    logging.info(
                        f"Transcription completed, length: {len(transcription)} chars"
                    )
                    return transcription

                except Exception as e:
                    logging.error(
                        f"Error processing audio file: {str(e)}", exc_info=True
                    )
                    await message.reply_text(
                        "Ocurrió un error al procesar el audio. Por favor, inténtalo de nuevo."
                    )
                    return None

        except Exception as e:
            logging.error(f"Error getting file: {str(e)}", exc_info=True)
            await message.reply_text(
                "No pude acceder al archivo de audio. Por favor, inténtalo de nuevo."
            )
            return None

    except Exception as e:
        logging.error(f"Error in audio handler: {str(e)}", exc_info=True)
        await message.reply_text(
            "Ocurrió un error inesperado. Por favor, inténtalo de nuevo."
        )
        return None
