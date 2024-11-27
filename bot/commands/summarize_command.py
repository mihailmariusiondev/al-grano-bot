from telegram.ext import CallbackContext
from telegram import Update
from bot.utils.decorators import (
    admin_command,
    log_command,
    bot_started,
    cooldown,
    premium_only,
)
from bot.utils.format_utils import format_recent_messages, send_long_message
from bot.utils.logger import logger
from bot.utils.get_message_type import get_message_type
from bot.utils.constants import YOUTUBE_REGEX, ARTICLE_URL_REGEX, MAX_RECENT_MESSAGES
from bot.services import db_service, openai_service
from bot.handlers.youtube_handler import youtube_handler
from bot.handlers.video_handler import video_handler
from bot.handlers.audio_handler import audio_handler
from bot.handlers.article_handler import article_handler
from bot.handlers.document_handler import document_handler
from bot.handlers.photo_handler import photo_handler
import random
import asyncio

ERROR_MESSAGES = {
    "NOT_ENOUGH_MESSAGES": "No hay suficientes mensajes para resumir. O me das 5 mensajes o te mando a la mierda",
    "ERROR_SUMMARIZING": "Error al resumir los mensajes. Ya la hemos liao... ",
    "ERROR_INVALID_YOUTUBE_URL": "URL de YouTube inválida. Eres tonto o qué?..",
    "ERROR_NOT_REPLYING_TO_MESSAGE": "No estás respondiendo a ningún mensaje. No me toques los co",
    "ERROR_TRANSCRIPT_DISABLED": "Transcripción deshabilitada para este vídeo. No me presiones tronco",
    "ERROR_CANNOT_SUMMARIZE_ARTICLE": "Pues va a ser que el artículo este no tiene chicha que resumir.",
    "ERROR_EMPTY_SUMMARY": "Error: El resumen está vacío. Parece que no había nada importante que decir, joder.",
    "ERROR_INVALID_SUMMARY": "Error: El resumen es inválido. Puede que haya entendido algo mal, coño.",
    "ERROR_UNKNOWN": "Error: Algo ha ido mal al resumir. No tengo ni puta idea de qué ha pasado.",
    "ERROR_PROCESSING_VIDEO_NOTE": "Error: No he podido procesar el video circular. Dale otra vez, figura.",
    "ERROR_PROCESSING_DOCUMENT": "Error: Este documento me ha dejado pillado. Prueba con otro formato, crack.",
    "ERROR_UNSUPPORTED_DOCUMENT": "Error: Este tipo de documento no lo manejo todavía, máquina.",
    "ERROR_NO_CAPTION": "Error: La foto no tiene texto que resumir, figura.",
    "ERROR_PROCESSING_POLL": "Error: No he podido procesar la encuesta. Prueba otra vez, crack.",
}

PROGRESS_MESSAGES = {
    "ANALYZING": "🔍 Analizando el contenido...",
    "DOWNLOADING": "⬇️ Descargando contenido...",
    "PROCESSING": "⚙️ Procesando datos...",
    "TRANSCRIBING": "🎯 Transcribiendo audio...",
    "SUMMARIZING": "🤖 Generando resumen...",
    "FETCHING_MESSAGES": "📚 Recopilando mensajes recientes...",
    "FORMATTING": "📝 Dando formato al resumen...",
    "FINALIZING": "✨ Finalizando...",
}

logger = logger.get_logger(__name__)

async def update_progress(message, text: str, delay: float = 0.5) -> None:
    """Update progress message with new status"""
    try:
        await asyncio.sleep(delay)  # Add small delay for better UX
        await message.edit_text(f"{text}")
    except Exception as e:
        logger.error(f"Error updating progress: {e}")

@admin_command()
@premium_only()
@log_command()
@bot_started()
@cooldown(60)
async def summarize_command(update: Update, context: CallbackContext):
    """Handle the /summarize command for different types of content"""
    try:
        # Get or create user
        user = update.effective_user
        await db_service.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        # Initial waiting message
        wait_message = await update.message.reply_text("⏳ Procesando tu solicitud...")

        # Case 1: No reply - summarize recent messages
        if not update.message.reply_to_message:
            await update_progress(wait_message, PROGRESS_MESSAGES["FETCHING_MESSAGES"])

            recent_messages = await db_service.get_recent_messages(
                update.effective_chat.id, MAX_RECENT_MESSAGES
            )
            if len(recent_messages) < 5:
                await wait_message.edit_text(ERROR_MESSAGES["NOT_ENOUGH_MESSAGES"])
                return

            await update_progress(wait_message, PROGRESS_MESSAGES["FORMATTING"])
            formatted_messages = format_recent_messages(recent_messages)

            await update_progress(wait_message, PROGRESS_MESSAGES["SUMMARIZING"])
            summary = await openai_service.get_summary(formatted_messages, "chat")

            await update_progress(wait_message, PROGRESS_MESSAGES["FINALIZING"])
            await send_long_message(update, summary)
            return

        # Case 2: Reply to message
        reply_msg = update.message.reply_to_message
        message_type = get_message_type(reply_msg)
        content = None
        summary_type = None

        try:
            # Handle different message types
            match message_type:
                case "text":
                    await update_progress(wait_message, PROGRESS_MESSAGES["ANALYZING"])
                    text = reply_msg.text or ""

                    if YOUTUBE_REGEX.search(text):
                        await update_progress(
                            wait_message, PROGRESS_MESSAGES["DOWNLOADING"]
                        )
                        content = await youtube_handler(update, context, text)
                        summary_type = "youtube"
                    elif ARTICLE_URL_REGEX.search(text):
                        await update_progress(
                            wait_message, PROGRESS_MESSAGES["DOWNLOADING"]
                        )
                        content = await article_handler(text)
                        summary_type = "web_article"
                    else:
                        content = text
                        summary_type = "quoted_message"

                case "voice" | "audio":
                    await update_progress(
                        wait_message, PROGRESS_MESSAGES["DOWNLOADING"]
                    )
                    await update_progress(
                        wait_message, PROGRESS_MESSAGES["TRANSCRIBING"]
                    )
                    content = await audio_handler(reply_msg, context)
                    summary_type = (
                        "voice_message" if message_type == "voice" else "audio_file"
                    )

                case "video" | "video_note":
                    await update_progress(
                        wait_message, PROGRESS_MESSAGES["DOWNLOADING"]
                    )
                    await update_progress(wait_message, PROGRESS_MESSAGES["PROCESSING"])
                    content = await video_handler(reply_msg, context)
                    summary_type = (
                        "video_note"
                        if message_type == "video_note"
                        else "telegram_video"
                    )

                case "document":
                    await update_progress(wait_message, PROGRESS_MESSAGES["ANALYZING"])
                    mime_type = reply_msg.document.mime_type
                    if mime_type:
                        try:
                            content = await document_handler(reply_msg, context)
                            if not content:
                                raise ValueError(
                                    "No se pudo extraer contenido del documento"
                                )
                            summary_type = "document"

                            # Procesar el contenido extraído
                            await update_progress(
                                wait_message, PROGRESS_MESSAGES["SUMMARIZING"]
                            )
                            summary = await openai_service.summarize_large_document(
                                content
                            )
                            await update_progress(
                                wait_message, PROGRESS_MESSAGES["FINALIZING"]
                            )
                            await send_long_message(update, summary)
                            return

                        except Exception as e:
                            logger.error(
                                f"Error procesando documento: {str(e)}", exc_info=True
                            )
                            await wait_message.edit_text(
                                f"Error procesando el documento: {str(e)}"
                            )
                            return

                case "photo":
                    await update_progress(wait_message, PROGRESS_MESSAGES["ANALYZING"])
                    content = await photo_handler(reply_msg, context)
                    summary_type = "photo"

                case "poll":
                    await update_progress(wait_message, PROGRESS_MESSAGES["PROCESSING"])
                    options = [opt.text for opt in reply_msg.poll.options]
                    content = f"Encuesta: {reply_msg.poll.question}\nOpciones: {', '.join(options)}"
                    summary_type = "quoted_message"

                case _:
                    await wait_message.edit_text(
                        f"No puedo resumir mensajes de tipo: {message_type}"
                    )
                    return

            if not content:
                await wait_message.edit_text(
                    ERROR_MESSAGES.get(
                        f"ERROR_CANNOT_SUMMARIZE_{message_type.upper()}",
                        ERROR_MESSAGES["ERROR_UNKNOWN"],
                    )
                )
                return

            # Generate summary
            await update_progress(wait_message, PROGRESS_MESSAGES["SUMMARIZING"])
            summary = await openai_service.get_summary(content, summary_type)

            # Send the final summary
            await update_progress(wait_message, PROGRESS_MESSAGES["FINALIZING"])
            await send_long_message(update, summary)

        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}", exc_info=True)
            await wait_message.edit_text(f"Error procesando el mensaje: {str(e)}")
            return

    except Exception as e:
        logger.error(f"Error in summarize_command: {e}", exc_info=True)
        await update.message.reply_text(f"Error al procesar la solicitud: {str(e)}")
