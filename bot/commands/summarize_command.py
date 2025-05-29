# bot/commands/summarize_command.py
from telegram.ext import CallbackContext
from telegram import Update
from telegram.constants import ParseMode
from bot.utils.decorators import (
    log_command,
    bot_started,
)
from bot.utils.format_utils import format_recent_messages, send_long_message, escape_markdown_v2
from bot.utils.logger import logger
from bot.utils.get_message_type import get_message_type
from bot.utils.constants import (
    YOUTUBE_REGEX, ARTICLE_URL_REGEX, MAX_RECENT_MESSAGES,
    COOLDOWN_TEXT_SIMPLE_SECONDS, COOLDOWN_ADVANCED_SECONDS,
    DAILY_LIMIT_ADVANCED_OPS, OPERATION_TYPE_TEXT_SIMPLE, OPERATION_TYPE_ADVANCED,
    MSG_DAILY_LIMIT_REACHED, MSG_COOLDOWN_ACTIVE
)
from bot.services import db_service, openai_service
from bot.handlers.youtube_handler import youtube_handler
from bot.handlers.video_handler import video_handler
from bot.handlers.audio_handler import audio_handler
from bot.handlers.article_handler import article_handler
from bot.handlers.document_handler import document_handler
import asyncio
from datetime import datetime,  date

ERROR_MESSAGES = {
    "NOT_ENOUGH_MESSAGES": "No hay suficientes mensajes para resumir. O me das 5 mensajes o te mando a la mierda",
    "ERROR_SUMMARIZING": "Error al resumir los mensajes. Ya la hemos liao...",
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
        await message.edit_text(f"{text}", parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(f"Error updating progress: {e}")

@log_command()
@bot_started()
async def summarize_command(update: Update, context: CallbackContext):
    """Handle the /summarize command with differentiated limits."""
    current_time_dt = datetime.now()
    current_date_val = current_time_dt.date()
    user_tg = update.effective_user
    chat_id = update.effective_chat.id
    wait_message = None
    try:
        user_db = await db_service.get_or_create_user(
            user_id=user_tg.id,
            username=user_tg.username,
            first_name=user_tg.first_name,
            last_name=user_tg.last_name,
        )
        is_admin_user = user_db.get("is_admin", False)
        operation_type = None

        # 1. Determine Operation Type
        if not update.message.reply_to_message:
            operation_type = OPERATION_TYPE_TEXT_SIMPLE  # Summarize chat history
        else:
            reply_msg = update.message.reply_to_message
            message_type_raw = get_message_type(reply_msg)
            if message_type_raw == "text":
                text_content = reply_msg.text or ""
                if YOUTUBE_REGEX.search(text_content) or ARTICLE_URL_REGEX.search(text_content):
                    operation_type = OPERATION_TYPE_ADVANCED
                else:
                    operation_type = OPERATION_TYPE_TEXT_SIMPLE
            elif message_type_raw in ["voice", "audio", "video", "video_note", "document"]:
                operation_type = OPERATION_TYPE_ADVANCED
            else:
                operation_type = OPERATION_TYPE_TEXT_SIMPLE # Treat as simple

        if not operation_type:
            await update.message.reply_text("No se pudo determinar el tipo de operación de resumen.", parse_mode=ParseMode.MARKDOWN_V2)
            return

        # 2. Apply Limits (if not admin)
        if not is_admin_user:
            # Daily Limit Reset for Advanced Ops
            if operation_type == OPERATION_TYPE_ADVANCED:
                advanced_op_reset_date_str = user_db.get("advanced_op_count_reset_date")
                advanced_op_reset_date = None
                if advanced_op_reset_date_str:
                    try:
                        advanced_op_reset_date = date.fromisoformat(advanced_op_reset_date_str)
                    except ValueError:
                        logger.error(f"Invalid date format for advanced_op_count_reset_date: {advanced_op_reset_date_str} for user {user_tg.id}")
                if advanced_op_reset_date != current_date_val:
                    await db_service.update_user_fields(
                        user_tg.id,
                        {
                            "advanced_op_today_count": 0,
                            "advanced_op_count_reset_date": current_date_val.isoformat(),
                        },
                    )
                    user_db["advanced_op_today_count"] = 0
                    user_db["advanced_op_count_reset_date"] = current_date_val.isoformat()
                    logger.info(f"Reset daily advanced op count for user {user_tg.id}")

            # Cooldown Check
            cooldown_seconds = 0
            last_op_time_str = None
            if operation_type == OPERATION_TYPE_TEXT_SIMPLE:
                cooldown_seconds = COOLDOWN_TEXT_SIMPLE_SECONDS
                last_op_time_str = user_db.get("last_text_simple_op_time")
            elif operation_type == OPERATION_TYPE_ADVANCED:
                cooldown_seconds = COOLDOWN_ADVANCED_SECONDS
                last_op_time_str = user_db.get("last_advanced_op_time")

            if last_op_time_str:
                last_op_time_dt = datetime.fromisoformat(last_op_time_str)
                elapsed_seconds = (current_time_dt - last_op_time_dt).total_seconds()
                if elapsed_seconds < cooldown_seconds:
                    remaining_cooldown = int(cooldown_seconds - elapsed_seconds)
                    await update.message.reply_text(
                        MSG_COOLDOWN_ACTIVE.format(remaining=remaining_cooldown), parse_mode=ParseMode.MARKDOWN_V2
                    )
                    return

            # Daily Limit Check for Advanced Ops
            if operation_type == OPERATION_TYPE_ADVANCED:
                current_advanced_ops = user_db.get("advanced_op_today_count", 0)
                if current_advanced_ops >= DAILY_LIMIT_ADVANCED_OPS:
                    await update.message.reply_text(
                        MSG_DAILY_LIMIT_REACHED.format(limit=DAILY_LIMIT_ADVANCED_OPS), parse_mode=ParseMode.MARKDOWN_V2
                    )
                    return

        wait_message = await update.message.reply_text("⏳ Procesando tu solicitud...", parse_mode=ParseMode.MARKDOWN_V2)

        # 3. Content Processing
        if not update.message.reply_to_message:
            await update_progress(wait_message, PROGRESS_MESSAGES["FETCHING_MESSAGES"])
            recent_messages = await db_service.get_recent_messages(
                chat_id, MAX_RECENT_MESSAGES
            )
            if len(recent_messages) < 5:
                await wait_message.edit_text(ERROR_MESSAGES["NOT_ENOUGH_MESSAGES"], parse_mode=ParseMode.MARKDOWN_V2)
                return
            await update_progress(wait_message, PROGRESS_MESSAGES["FORMATTING"])
            formatted_messages = format_recent_messages(recent_messages)
            chat_state_db = await db_service.get_chat_state(chat_id)
            summary_style = (
                "chat_long"
                if chat_state_db.get("summary_type", "long") == "long"
                else "chat_short"
            )
            await update_progress(wait_message, PROGRESS_MESSAGES["SUMMARIZING"])
            summary = await openai_service.get_summary(
                content=formatted_messages,
                summary_type=summary_style, # This is 'chat_long' or 'chat_short', not from SUMMARY_PROMPTS directly
                language="Spanish",
            )
            await update_progress(wait_message, PROGRESS_MESSAGES["FINALIZING"])
            await send_long_message(update, summary)
        else:
            reply_msg = update.message.reply_to_message
            message_type_for_handler = get_message_type(reply_msg)
            content_for_summary = None
            summary_type_for_openai = None
            try:
                match message_type_for_handler:
                    case "text":
                        await update_progress(wait_message, PROGRESS_MESSAGES["ANALYZING"])
                        text = reply_msg.text or ""
                        if YOUTUBE_REGEX.search(text):
                            await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                            content_for_summary = await youtube_handler(update, context, text)
                            summary_type_for_openai = "youtube"
                        elif ARTICLE_URL_REGEX.search(text):
                            await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                            content_for_summary = await article_handler(text)
                            summary_type_for_openai = "web_article"
                        else:
                            content_for_summary = text
                            summary_type_for_openai = "quoted_message"
                    case "voice" | "audio":
                        await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                        await update_progress(wait_message, PROGRESS_MESSAGES["TRANSCRIBING"])
                        content_for_summary = await audio_handler(reply_msg, context)
                        summary_type_for_openai = "voice_message" if message_type_for_handler == "voice" else "audio_file"
                    case "video" | "video_note":
                        await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                        await update_progress(wait_message, PROGRESS_MESSAGES["PROCESSING"])
                        content_for_summary = await video_handler(reply_msg, context)
                        summary_type_for_openai = "video_note" if message_type_for_handler == "video_note" else "telegram_video"
                    case "document":
                        await update_progress(wait_message, PROGRESS_MESSAGES["ANALYZING"])
                        content_for_summary = await document_handler(reply_msg, context)
                        if not content_for_summary:
                            raise ValueError("No se pudo extraer contenido del documento")
                        summary_type_for_openai = "document"
                        await update_progress(wait_message, PROGRESS_MESSAGES["SUMMARIZING"])
                        summary = await openai_service.summarize_large_document(content_for_summary)
                        await update_progress(wait_message, PROGRESS_MESSAGES["FINALIZING"])
                        await send_long_message(update, summary)
                        content_for_summary = None  # Mark as processed
                    case _:
                        await wait_message.edit_text(
                            "Este tipo de mensaje no lo puedo resumir crack. Intenta con mensajes de texto, enlaces a YouTube o artículos web, mensajes de voz, archivos de audio, vídeos o documentos (PDF, DOCX, TXT).", parse_mode=ParseMode.MARKDOWN_V2
                        )
                        return

                if content_for_summary and summary_type_for_openai:
                    if not content_for_summary.strip():
                        await wait_message.edit_text(
                            ERROR_MESSAGES.get(
                                f"ERROR_CANNOT_SUMMARIZE_{message_type_for_handler.upper()}",
                                ERROR_MESSAGES["ERROR_EMPTY_SUMMARY"],
                            ), parse_mode=ParseMode.MARKDOWN_V2
                        )
                        return
                    await update_progress(wait_message, PROGRESS_MESSAGES["SUMMARIZING"])
                    summary = await openai_service.get_summary(content_for_summary, summary_type_for_openai)
                    await update_progress(wait_message, PROGRESS_MESSAGES["FINALIZING"])
                    await send_long_message(update, summary)
                elif summary_type_for_openai == "document" and not content_for_summary:
                    pass
                elif not content_for_summary and summary_type_for_openai != "document":
                    await wait_message.edit_text(
                        ERROR_MESSAGES.get(
                            f"ERROR_CANNOT_SUMMARIZE_{message_type_for_handler.upper()}",
                            ERROR_MESSAGES["ERROR_UNKNOWN"],
                        ), parse_mode=ParseMode.MARKDOWN_V2
                    )
                    return
            except Exception as e:
                logger.error(f"Error procesando mensaje: {str(e)}", exc_info=True)
                if wait_message:
                    await wait_message.edit_text(f"Error procesando el mensaje: {escape_markdown_v2(str(e))}", parse_mode=ParseMode.MARKDOWN_V2)
                else:
                    await update.message.reply_text(f"Error procesando el mensaje: {escape_markdown_v2(str(e))}", parse_mode=ParseMode.MARKDOWN_V2)
                return

        # 4. Update Usage Data (if not admin)
        if not is_admin_user:
            fields_to_update = {}
            if operation_type == OPERATION_TYPE_TEXT_SIMPLE:
                fields_to_update["last_text_simple_op_time"] = current_time_dt.isoformat()
            elif operation_type == OPERATION_TYPE_ADVANCED:
                fields_to_update["last_advanced_op_time"] = current_time_dt.isoformat()
                fields_to_update["advanced_op_today_count"] = user_db.get("advanced_op_today_count", 0) + 1
            if fields_to_update:
                await db_service.update_user_fields(user_tg.id, fields_to_update)
                logger.info(f"Updated usage data for user {user_tg.id}, operation: {operation_type}")

        if wait_message:
            try:
                await wait_message.delete()
            except Exception as e_del:
                logger.warning(f"Could not delete wait_message: {e_del}")
    except Exception as e:
        logger.error(f"Error in summarize_command: {e}", exc_info=True)
        if wait_message:
            await wait_message.edit_text(f"Error al procesar la solicitud: {escape_markdown_v2(str(e))}", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text(f"Error al procesar la solicitud: {escape_markdown_v2(str(e))}", parse_mode=ParseMode.MARKDOWN_V2)
