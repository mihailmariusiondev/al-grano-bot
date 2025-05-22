from datetime import datetime
from telegram.ext import CallbackContext
from telegram import Update
from bot.utils.decorators import (
    log_command,
    bot_started,
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


@log_command()
@bot_started()
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

        # A. Fetch User and Admin Status
        db_user = await db_service.get_user(user.id)
        if not db_user:
            await update.message.reply_text("Error: Could not retrieve user data. Please try again later.")
            return

        is_admin_user = db_user.get('is_admin', False)
        is_premium_user = db_user.get('is_premium', False)
        
        # A. Fetch and Prepare Rate Limit Data
        last_text_summary_time_str = db_user.get('last_text_summary_time')
        last_media_summary_time_str = db_user.get('last_media_summary_time')
        media_summary_daily_count = db_user.get('media_summary_daily_count', 0)
        media_summary_last_reset_str = db_user.get('media_summary_last_reset')

        now = datetime.now()
        last_text_summary_time = datetime.fromisoformat(last_text_summary_time_str) if last_text_summary_time_str else None
        last_media_summary_time = datetime.fromisoformat(last_media_summary_time_str) if last_media_summary_time_str else None
        media_summary_last_reset = datetime.fromisoformat(media_summary_last_reset_str) if media_summary_last_reset_str else None

        # B. Determine User Tier
        user_tier = "FREE"
        if is_admin_user:
            user_tier = "ADMIN"
        elif is_premium_user:
            user_tier = "PREMIUM"

        content_category = None # Will be set below

        # Case 1: No reply - summarize recent messages
        if not update.message.reply_to_message:
            # C. Determine Content Category (Chat History)
            content_category = "TEXT_SUMMARY" # Summarizing chat history is a text summary
            
            # D. Implement Access Control Logic (already present and correct)
            if user_tier == "FREE" and content_category == "MEDIA_SUMMARY": # This specific check for MEDIA_SUMMARY on FREE tier is fine here
                await update.message.reply_text("Summarizing media (audio, video, documents, URLs, etc.) is a premium feature. Free users can only summarize text messages and chat history.")
                return

            # B. Implement Daily Media Counter Reset (for chat history context, though less relevant here as it's TEXT_SUMMARY)
            if user_tier != "ADMIN":
                if media_summary_last_reset is None or (now - media_summary_last_reset).days >= 1:
                    media_summary_daily_count = 0
                    # media_summary_last_reset will be updated upon successful media summary
                    pass

            # C. Implement Dynamic Rate Limiting Logic
            if user_tier != "ADMIN": # Admins bypass rate limits
                cooldown_seconds = 0
                limit_type = ""

                if content_category == "TEXT_SUMMARY":
                    cooldown_seconds = 30 if user_tier == "PREMIUM" else 120 # Premium: 30s, Free: 120s
                    if last_text_summary_time and (now - last_text_summary_time).total_seconds() < cooldown_seconds:
                        limit_type = "TEXT"
                # MEDIA_SUMMARY is not possible here for FREE users due to earlier check

                if limit_type:
                    remaining_time = int(cooldown_seconds - (now - last_text_summary_time).total_seconds())
                    await update.message.reply_text(f"Please wait {remaining_time}s before trying to summarize {limit_type.lower()} content again.")
                    return
            
            wait_message = await update.message.reply_text("⏳ Procesando tu solicitud...")
            await update_progress(wait_message, PROGRESS_MESSAGES["FETCHING_MESSAGES"])

            recent_messages = await db_service.get_recent_messages(
                update.effective_chat.id, MAX_RECENT_MESSAGES
            )
            if len(recent_messages) < 5:
                await wait_message.edit_text(ERROR_MESSAGES["NOT_ENOUGH_MESSAGES"])
                return

            await update_progress(wait_message, PROGRESS_MESSAGES["FORMATTING"])
            formatted_messages = format_recent_messages(recent_messages)

            # Get chat state to determine summary type
            chat_state = await db_service.get_chat_state(update.effective_chat.id)
            summary_type = (
                "chat_long"
                if chat_state.get("summary_type", "long") == "long"
                else "chat_short"
            )

            await update_progress(wait_message, PROGRESS_MESSAGES["SUMMARIZING"])
            summary = await openai_service.get_summary(
                content=formatted_messages,
                summary_type=summary_type,
                language="Spanish",
            )

            await update_progress(wait_message, PROGRESS_MESSAGES["FINALIZING"])
            await send_long_message(update, summary)
            
            # D. Update Rate Limit State in Database (on successful summary)
            if user_tier != "ADMIN":
                await db_service.update_user_summary_rate_limit_data(
                    user_id=user.id,
                    last_text_summary_time=now.isoformat()
                )
            return

        # Case 2: Reply to message
        else: # This is the start of the existing else block for replies
            reply_msg = update.message.reply_to_message
            message_type = get_message_type(reply_msg)

            # C. Determine Content Category (Replies)
            content_category = "TEXT_SUMMARY" # Default, will be overridden for media
            if message_type in ["voice", "audio", "video", "video_note", "document", "photo"]:
                content_category = "MEDIA_SUMMARY"
            elif message_type == "text":
                text_content = reply_msg.text or ""
                if YOUTUBE_REGEX.search(text_content) or ARTICLE_URL_REGEX.search(text_content):
                    content_category = "MEDIA_SUMMARY" # URLs are media
                else:
                    content_category = "TEXT_SUMMARY" # Plain text reply
            else: # polls or other types
                content_category = "TEXT_SUMMARY"

            # D. Implement Access Control Logic (already present and correct)
            if user_tier == "FREE" and content_category == "MEDIA_SUMMARY":
                await update.message.reply_text("Summarizing media (audio, video, documents, URLs, etc.) is a premium feature. Free users can only summarize text messages and chat history.")
                return

            # B. Implement Daily Media Counter Reset
            if user_tier != "ADMIN": # Admins are not subject to this reset for counting purposes
                if media_summary_last_reset is None or (now - media_summary_last_reset).days >= 1:
                    media_summary_daily_count = 0
                    # media_summary_last_reset will be updated upon successful media summary
                    pass 

            # C. Implement Dynamic Rate Limiting Logic
            if user_tier != "ADMIN": # Admins bypass rate limits
                cooldown_seconds = 0
                limit_type = ""

                if content_category == "TEXT_SUMMARY":
                    cooldown_seconds = 30 if user_tier == "PREMIUM" else 120 # Premium: 30s, Free: 120s
                    if last_text_summary_time and (now - last_text_summary_time).total_seconds() < cooldown_seconds:
                        limit_type = "TEXT"
                elif content_category == "MEDIA_SUMMARY": # This will mostly apply to PREMIUM users due to earlier access control
                    cooldown_seconds = 120 # Premium: 120s (2 minutes)
                    # Free users are blocked from MEDIA_SUMMARY by prior access control.
                    if last_media_summary_time and (now - last_media_summary_time).total_seconds() < cooldown_seconds:
                        limit_type = "MEDIA"

                if limit_type:
                    relevant_last_time = last_text_summary_time if limit_type == "TEXT" else last_media_summary_time
                    remaining_time = int(cooldown_seconds - (now - relevant_last_time).total_seconds())
                    await update.message.reply_text(f"Please wait {remaining_time}s before trying to summarize {limit_type.lower()} content again.")
                    return

            wait_message = await update.message.reply_text("⏳ Procesando tu solicitud...")
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
            
            # D. Update Rate Limit State in Database (on successful summary)
            if user_tier != "ADMIN":
                if content_category == "TEXT_SUMMARY":
                    await db_service.update_user_summary_rate_limit_data(
                        user_id=user.id,
                        last_text_summary_time=now.isoformat()
                    )
                elif content_category == "MEDIA_SUMMARY":
                    new_media_summary_last_reset_iso = None
                    if media_summary_last_reset is None or (now - media_summary_last_reset).days >= 1:
                        new_media_summary_last_reset_iso = now.isoformat()
                    elif isinstance(media_summary_last_reset, datetime): # if it was already a datetime object from db
                        new_media_summary_last_reset_iso = media_summary_last_reset.isoformat()
                    else: # it was already an ISO string
                        new_media_summary_last_reset_iso = media_summary_last_reset

                    await db_service.update_user_summary_rate_limit_data(
                        user_id=user.id,
                        last_media_summary_time=now.isoformat(),
                        media_summary_daily_count=media_summary_daily_count + 1,
                        media_summary_last_reset=new_media_summary_last_reset_iso
                    )

        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}", exc_info=True)
            await wait_message.edit_text(f"Error procesando el mensaje: {str(e)}")
            return

    except Exception as e:
        logger.error(f"Error in summarize_command: {e}", exc_info=True)
        await update.message.reply_text(f"Error al procesar la solicitud: {str(e)}")
