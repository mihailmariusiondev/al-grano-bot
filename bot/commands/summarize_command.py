# bot/commands/summarize_command.py
from telegram.ext import CallbackContext
from telegram import Update
from bot.utils.decorators import (
    log_command,
    bot_started,
)
from bot.utils.format_utils import format_recent_messages, send_long_message
from bot.utils.logger import logger
from bot.utils.get_message_type import get_message_type
from bot.utils.constants import (
    YOUTUBE_REGEX, ARTICLE_URL_REGEX, MAX_RECENT_MESSAGES,
    COOLDOWN_TEXT_SIMPLE_SECONDS, COOLDOWN_ADVANCED_SECONDS,
    DAILY_LIMIT_ADVANCED_OPS, OPERATION_TYPE_TEXT_SIMPLE, OPERATION_TYPE_ADVANCED,
    MSG_DAILY_LIMIT_REACHED, MSG_COOLDOWN_ACTIVE, get_button_label
)
from bot.constants import USER_ERROR_MESSAGES, COMMAND_MESSAGES
from bot.services import db_service, openai_service
from bot.handlers.youtube_handler import youtube_handler
from bot.handlers.video_handler import video_handler
from bot.handlers.audio_handler import audio_handler
from bot.handlers.article_handler import article_handler
from bot.handlers.document_handler import document_handler
import asyncio
from datetime import datetime,  date

from bot.utils.admin_notifications import (
    notify_admins_critical, 
    notify_admins_service_error, 
    notify_admins_rate_limit
)

# Legacy error messages - converted to user-friendly messages
LOCAL_MESSAGES = {
    "NOT_ENOUGH_MESSAGES": "No hay suficientes mensajes para resumir.",
    "EMPTY_SUMMARY": "El contenido no pudo ser procesado completamente.",
    "INVALID_SUMMARY": "Hubo un problema procesando el contenido.",
    "PROCESSING_FAILED": "No pude procesar este tipo de contenido."
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
    """Handle the /summarize command with differentiated limits."""
    current_time_dt = datetime.now()
    current_date_val = current_time_dt.date()
    user_tg = update.effective_user
    chat_id = update.effective_chat.id
    wait_message = None

    logger.debug(f"=== SUMMARIZE COMMAND STARTED ===")
    logger.debug(f"User ID: {user_tg.id}, Username: {user_tg.username}")
    logger.debug(f"Chat ID: {chat_id}, Current time: {current_time_dt}")
    logger.debug(f"Has reply message: {update.message.reply_to_message is not None}")

    try:
        user_db = await db_service.get_or_create_user(
            user_id=user_tg.id,
            username=user_tg.username,
            first_name=user_tg.first_name,
            last_name=user_tg.last_name,
        )
        is_admin_user = user_db.get("is_admin", False)
        operation_type = None

        logger.debug(f"User DB data: {user_db}")
        logger.debug(f"Is admin user: {is_admin_user}")

        # 1. Determine Operation Type
        if not update.message.reply_to_message:
            operation_type = OPERATION_TYPE_TEXT_SIMPLE  # Summarize chat history
            logger.debug(f"No reply message -> Operation type: {operation_type}")
        else:
            reply_msg = update.message.reply_to_message
            message_type_raw = get_message_type(reply_msg)
            logger.debug(f"Reply message detected. Message type: {message_type_raw}")

            if message_type_raw == "text":
                text_content = reply_msg.text or ""
                logger.debug(f"Text content length: {len(text_content)}")
                logger.debug(f"Text content preview: {text_content[:100]}...")

                if YOUTUBE_REGEX.search(text_content) or ARTICLE_URL_REGEX.search(text_content):
                    operation_type = OPERATION_TYPE_ADVANCED
                    logger.debug(f"URL detected in text -> Operation type: {operation_type}")
                else:
                    operation_type = OPERATION_TYPE_TEXT_SIMPLE
                    logger.debug(f"Plain text detected -> Operation type: {operation_type}")
            elif message_type_raw in ["voice", "audio", "video", "video_note", "document"]:
                operation_type = OPERATION_TYPE_ADVANCED
                logger.debug(f"Media message detected -> Operation type: {operation_type}")
            else:
                operation_type = OPERATION_TYPE_TEXT_SIMPLE # Treat as simple
                logger.debug(f"Unknown message type, treating as simple -> Operation type: {operation_type}")

        if not operation_type:
            logger.error("Could not determine operation type")
            await update.message.reply_text(COMMAND_MESSAGES["SUMMARIZE"]["NO_CONTENT"])
            return

        logger.info(f"Final operation type determined: {operation_type}")

        # 2. Apply Limits (if not admin)
        if not is_admin_user:
            logger.debug("User is not admin, applying limits")
            # Daily Limit Reset for Advanced Ops
            if operation_type == OPERATION_TYPE_ADVANCED:
                logger.debug("Checking advanced operation limits")
                advanced_op_reset_date_str = user_db.get("advanced_op_count_reset_date")
                advanced_op_reset_date = None
                logger.debug(f"Advanced op reset date string: {advanced_op_reset_date_str}")

                if advanced_op_reset_date_str:
                    try:
                        advanced_op_reset_date = date.fromisoformat(advanced_op_reset_date_str)
                        logger.debug(f"Parsed reset date: {advanced_op_reset_date}")
                    except ValueError:
                        logger.error(f"Invalid date format for advanced_op_count_reset_date: {advanced_op_reset_date_str} for user {user_tg.id}")

                if advanced_op_reset_date != current_date_val:
                    logger.info(f"Resetting daily count for user {user_tg.id} (last reset: {advanced_op_reset_date}, current: {current_date_val})")
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
                else:
                    logger.debug(f"No reset needed for user {user_tg.id}, same date")

            # Cooldown Check
            cooldown_seconds = 0
            last_op_time_str = None
            if operation_type == OPERATION_TYPE_TEXT_SIMPLE:
                cooldown_seconds = COOLDOWN_TEXT_SIMPLE_SECONDS
                last_op_time_str = user_db.get("last_text_simple_op_time")
                logger.debug(f"Text simple cooldown: {cooldown_seconds}s, last op: {last_op_time_str}")
            elif operation_type == OPERATION_TYPE_ADVANCED:
                cooldown_seconds = COOLDOWN_ADVANCED_SECONDS
                last_op_time_str = user_db.get("last_advanced_op_time")
                logger.debug(f"Advanced cooldown: {cooldown_seconds}s, last op: {last_op_time_str}")

            if last_op_time_str:
                last_op_time_dt = datetime.fromisoformat(last_op_time_str)
                elapsed_seconds = (current_time_dt - last_op_time_dt).total_seconds()
                logger.debug(f"Elapsed since last op: {elapsed_seconds}s")

                if elapsed_seconds < cooldown_seconds:
                    remaining_cooldown = int(cooldown_seconds - elapsed_seconds)
                    logger.info(f"Cooldown active for user {user_tg.id}: {remaining_cooldown}s remaining")
                    await update.message.reply_text(
                        MSG_COOLDOWN_ACTIVE.format(remaining=remaining_cooldown)
                    )
                    return
                else:
                    logger.debug(f"Cooldown passed for user {user_tg.id}")

            # Daily Limit Check for Advanced Ops
            if operation_type == OPERATION_TYPE_ADVANCED:
                current_advanced_ops = user_db.get("advanced_op_today_count", 0)
                logger.debug(f"Current advanced ops today: {current_advanced_ops}/{DAILY_LIMIT_ADVANCED_OPS}")

                if current_advanced_ops >= DAILY_LIMIT_ADVANCED_OPS:
                    logger.info(f"Daily limit reached for user {user_tg.id}: {current_advanced_ops}/{DAILY_LIMIT_ADVANCED_OPS}")
                    await update.message.reply_text(
                        MSG_DAILY_LIMIT_REACHED.format(limit=DAILY_LIMIT_ADVANCED_OPS)
                    )
                    return
        else:
            logger.debug("User is admin, skipping all limits")

        wait_message = await update.message.reply_text(COMMAND_MESSAGES["SUMMARIZE"]["PROCESSING"])
        logger.debug("Wait message sent, starting content processing")

        # 3. Content Processing
        if not update.message.reply_to_message:
            logger.debug("Processing chat history (no reply message)")
            await update_progress(wait_message, PROGRESS_MESSAGES["FETCHING_MESSAGES"])
            recent_messages = await db_service.get_recent_messages(
                chat_id, MAX_RECENT_MESSAGES
            )
            logger.debug(f"Fetched {len(recent_messages)} recent messages")

            if len(recent_messages) < 5:
                logger.warning(f"Not enough messages ({len(recent_messages)}) for summary")
                await wait_message.edit_text(COMMAND_MESSAGES["SUMMARIZE"]["NO_CONTENT"])
                return

            await update_progress(wait_message, PROGRESS_MESSAGES["FORMATTING"])
            formatted_messages = format_recent_messages(recent_messages)
            logger.debug(f"Formatted messages length: {len(formatted_messages)} chars")

            chat_config = await db_service.get_chat_summary_config(chat_id)
            logger.debug(f"Chat config: {chat_config}")

            await update_progress(wait_message, PROGRESS_MESSAGES["SUMMARIZING"])
            try:
                logger.info("Calling OpenAI service for chat summary")
                summary = await openai_service.get_summary(
                    content=formatted_messages,
                    summary_type="chat",
                    summary_config=chat_config
                )
                logger.debug(f"Summary generated, length: {len(summary)} chars")

                # Obtener el nombre del tono en el idioma correcto
                tone_key = chat_config.get("tone", "neutral")
                lang_key = chat_config.get("language", "es")
                tone_name = get_button_label("tone", tone_key, lang_key)

                # Prepend the tone to the summary
                final_summary = f"🧠 *Tono: {tone_name}*\n\n{summary}"

            except ValueError as e:
                logger.error(f"ValueError in summary generation: {e}")
                # Handle unsupported language
                if "is not supported" in str(e):
                    await wait_message.edit_text(COMMAND_MESSAGES["SUMMARIZE"]["LANGUAGE_ERROR"])
                    return
                else:
                    await wait_message.edit_text(USER_ERROR_MESSAGES["PROCESSING_ERROR"])
                    return
            except Exception as e:
                logger.error(f"Unexpected error in summary generation: {e}", exc_info=True)
                await wait_message.edit_text(USER_ERROR_MESSAGES["GENERAL_ERROR"])
                return

            await update_progress(wait_message, PROGRESS_MESSAGES["FINALIZING"])
            await send_long_message(update, final_summary)
            logger.info("Chat history summary completed successfully")
        else:
            logger.debug("Processing reply message")
            reply_msg = update.message.reply_to_message
            message_type_for_handler = get_message_type(reply_msg)
            content_for_summary = None
            summary_type = None # Renamed from summary_type_for_openai

            logger.debug(f"Reply message type: {message_type_for_handler}")
            logger.debug(f"Reply message ID: {reply_msg.message_id}")

            try:
                match message_type_for_handler:
                    case "text":
                        logger.debug("Processing text reply message")
                        await update_progress(wait_message, PROGRESS_MESSAGES["ANALYZING"])
                        text = reply_msg.text or ""
                        logger.debug(f"Text content length: {len(text)}")

                        if YOUTUBE_REGEX.search(text):
                            logger.info("YouTube URL detected in text")
                            await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                            content_for_summary = await youtube_handler(update, context, text)
                            summary_type = "youtube"
                            logger.debug(f"YouTube content extracted, length: {len(content_for_summary) if content_for_summary else 0}")
                        elif ARTICLE_URL_REGEX.search(text):
                            logger.info("Article URL detected in text")
                            await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                            content_for_summary = await article_handler(text)
                            summary_type = "web_article"
                            logger.debug(f"Article content extracted, length: {len(content_for_summary) if content_for_summary else 0}")
                        else:
                            logger.debug("Plain text message, no URLs detected")
                            content_for_summary = text
                            summary_type = "quoted_message"
                    case "voice" | "audio":
                        logger.info(f"Processing {message_type_for_handler} message")
                        await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                        await update_progress(wait_message, PROGRESS_MESSAGES["TRANSCRIBING"])
                        content_for_summary = await audio_handler(reply_msg, context)
                        summary_type = "voice_message" if message_type_for_handler == "voice" else "audio_file"
                        logger.debug(f"Audio transcribed, length: {len(content_for_summary) if content_for_summary else 0}")

                    case "video" | "video_note":
                        logger.info(f"Processing {message_type_for_handler} message")
                        await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                        await update_progress(wait_message, PROGRESS_MESSAGES["PROCESSING"])
                        content_for_summary = await video_handler(reply_msg, context)
                        summary_type = "video_note" if message_type_for_handler == "video_note" else "telegram_video"
                        logger.debug(f"Video processed, length: {len(content_for_summary) if content_for_summary else 0}")

                    case "document":
                        logger.info("Processing document message")
                        summary_type = "document" # Set summary_type for document
                        await update_progress(wait_message, PROGRESS_MESSAGES["ANALYZING"])
                        content_for_summary = await document_handler(reply_msg, context)
                        if not content_for_summary:
                            logger.error("Document handler returned empty content")
                            raise ValueError("No se pudo extraer contenido del documento")

                        logger.debug(f"Document content extracted, length: {len(content_for_summary)}")
                        await update_progress(wait_message, PROGRESS_MESSAGES["SUMMARIZING"])

                        logger.info("Calling summarize_large_document")
                        summary = await openai_service.summarize_large_document(content_for_summary)
                        logger.debug(f"Document summary generated, length: {len(summary)}")

                        await update_progress(wait_message, PROGRESS_MESSAGES["FINALIZING"])
                        await send_long_message(update, summary)
                        content_for_summary = None  # Mark as processed, so the general summary call is skipped
                        logger.info("Document summary completed successfully")

                    case _:
                        logger.warning(f"Unsupported message type: {message_type_for_handler}")
                        await wait_message.edit_text(
                            "Este tipo de mensaje no lo puedo resumir crack. Intenta con mensajes de texto, enlaces a YouTube o artículos web, mensajes de voz, archivos de audio, vídeos o documentos (PDF, DOCX, TXT)."
                        )
                        return

                if content_for_summary and summary_type: # Use summary_type here
                    logger.debug(f"Processing summary for type: {summary_type}")
                    if not content_for_summary.strip():
                        logger.warning(f"Empty content for summary type: {summary_type}")
                        await wait_message.edit_text(
                            ERROR_MESSAGES.get(
                                f"ERROR_CANNOT_SUMMARIZE_{message_type_for_handler.upper()}",
                                USER_ERROR_MESSAGES["PROCESSING_ERROR"],
                            )
                        )
                        return
                    # Para todos los resúmenes de reply, la config del chat se usa para el idioma.
                    # Los modificadores de tono/longitud/etc no se aplican, según el nuevo diseño.
                    reply_config = await db_service.get_chat_summary_config(chat_id)
                    logger.debug(f"Reply config: {reply_config}")

                    await update_progress(wait_message, PROGRESS_MESSAGES["SUMMARIZING"])
                    logger.info(f"Calling OpenAI service for {summary_type} summary")
                    summary = await openai_service.get_summary(content_for_summary, summary_type, reply_config)
                    logger.debug(f"Reply summary generated, length: {len(summary)}")

                    # Obtener el nombre del tono en el idioma correcto
                    tone_key = reply_config.get("tone", "neutral")
                    lang_key = reply_config.get("language", "es")
                    tone_name = get_button_label("tone", tone_key, lang_key)
                    final_summary = f"🧠 *Tono: {tone_name}*\n\n{summary}"

                    await update_progress(wait_message, PROGRESS_MESSAGES["FINALIZING"])
                    await send_long_message(update, summary)
                    logger.info(f"Reply message summary completed successfully for type: {summary_type}")

                elif summary_type == "document" and not content_for_summary: # Use summary_type here
                    logger.debug("Document was already processed by summarize_large_document")
                    pass # Document was handled by summarize_large_document
                elif not content_for_summary and summary_type != "document": # Use summary_type here
                    logger.error(f"No content extracted for summary type: {summary_type}")
                    await wait_message.edit_text(
                        ERROR_MESSAGES.get(
                            f"ERROR_CANNOT_SUMMARIZE_{message_type_for_handler.upper()}",
                            USER_ERROR_MESSAGES["GENERAL_ERROR"],
                        )
                    )
                    return
            except Exception as e:
                logger.error(f"Error procesando mensaje: {str(e)}", exc_info=True)
                await notify_admins_service_error(
                    context, "Message Processing", str(e),
                    user_tg.id if user_tg else None, update.effective_chat.id
                )
                if wait_message:
                    await wait_message.edit_text(USER_ERROR_MESSAGES["PROCESSING_ERROR"])
                else:
                    await update.message.reply_text(USER_ERROR_MESSAGES["PROCESSING_ERROR"])
                return

        # 4. Update Usage Data (if not admin)
        if not is_admin_user:
            logger.debug("Updating usage data for non-admin user")
            fields_to_update = {}
            if operation_type == OPERATION_TYPE_TEXT_SIMPLE:
                fields_to_update["last_text_simple_op_time"] = current_time_dt.isoformat()
                logger.debug(f"Recording text simple operation at {current_time_dt.isoformat()}")
            elif operation_type == OPERATION_TYPE_ADVANCED:
                fields_to_update["last_advanced_op_time"] = current_time_dt.isoformat()
                new_count = user_db.get("advanced_op_today_count", 0) + 1
                fields_to_update["advanced_op_today_count"] = new_count
                logger.debug(f"Recording advanced operation at {current_time_dt.isoformat()}, new count: {new_count}")

            if fields_to_update:
                await db_service.update_user_fields(user_tg.id, fields_to_update)
                logger.info(f"Updated usage data for user {user_tg.id}, operation: {operation_type}, fields: {fields_to_update}")
        else:
            logger.debug("Admin user, skipping usage data update")

        if wait_message:
            try:
                await wait_message.delete()
                logger.debug("Wait message deleted successfully")
            except Exception as e_del:
                logger.warning(f"Could not delete wait_message: {e_del}")

        logger.info(f"=== SUMMARIZE COMMAND COMPLETED SUCCESSFULLY FOR USER {user_tg.id} ===")

    except Exception as e:
        logger.error(f"=== SUMMARIZE COMMAND FAILED FOR USER {user_tg.id if user_tg else 'UNKNOWN'} ===")
        logger.error(f"Error in summarize_command: {e}", exc_info=True)
        await notify_admins_critical(
            context, "Summarize Command Failed", str(e),
            user_tg.id if user_tg else None, update.effective_chat.id
        )
        if wait_message:
            try:
                await wait_message.edit_text(USER_ERROR_MESSAGES["GENERAL_ERROR"])
            except Exception as edit_error:
                logger.error(f"Could not edit wait message with error: {edit_error}")
        else:
            try:
                await update.message.reply_text(USER_ERROR_MESSAGES["GENERAL_ERROR"])
            except Exception as reply_error:
                logger.error(f"Could not send error message: {reply_error}")
