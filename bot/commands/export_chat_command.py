from datetime import datetime, timedelta
import json
import tempfile
import os
import pytz
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command, bot_started
from bot.services.database_service import db_service
from bot.utils.logger import logger
from bot.utils.constants import EXPORT_PROGRESS_BATCH_SIZE

# Consistent with other commands
logger = logger.get_logger(__name__)

# Error messages following the project pattern
ERROR_MESSAGES = {
    "NO_MESSAGES": "No hay mensajes para exportar hoy.",
    "EXPORT_ERROR": "❌ Error al exportar el chat.",
    "FILE_CREATION_ERROR": "❌ Error al crear el archivo de exportación.",
    "SEND_ERROR": "❌ Error al enviar el archivo."
}

SUCCESS_MESSAGES = {
    "EXPORT_SUCCESS": "✅ Chat exportado exitosamente.",
    "FILE_READY": "📄 Archivo de exportación listo."
}


def build_conversation_threads(messages):
    """Build conversation threads by grouping replies together"""
    threads = {}
    standalone_messages = []

    # First pass: identify all message IDs
    all_message_ids = {msg.get("telegram_message_id") for msg in messages}

    # Second pass: organize into threads
    for msg in messages:
        reply_to = msg.get("telegram_reply_to_message_id")
        msg_id = msg.get("telegram_message_id")

        if reply_to and reply_to in all_message_ids:
            # This is a reply to a message in our dataset
            if reply_to not in threads:
                threads[reply_to] = {
                    "original_message": None,
                    "replies": []
                }
            threads[reply_to]["replies"].append(msg)
        elif reply_to:
            # Reply to a message not in our dataset (older message)
            standalone_messages.append(msg)
        else:
            # Original message or standalone
            if msg_id in threads:
                threads[msg_id]["original_message"] = msg
            else:
                standalone_messages.append(msg)

    return threads, standalone_messages


def format_for_ai_analysis(messages, chat_id, export_time):
    """Format messages in an AI-friendly structure for analysis"""
    madrid_tz = pytz.timezone("Europe/Madrid")

    # Basic statistics
    total_messages = len(messages)
    users = {}
    time_range = {"start": None, "end": None}

    # Collect user stats and time range
    for msg in messages:
        user_id = msg.get("user_id")
        username = msg.get("username") or msg.get("first_name") or str(user_id)

        if user_id not in users:
            users[user_id] = {
                "name": username,
                "message_count": 0,
                "first_message_time": None,
                "last_message_time": None
            }

        users[user_id]["message_count"] += 1

        # Parse timestamp
        try:
            created_utc = datetime.fromisoformat(msg["created_at"]).replace(tzinfo=pytz.UTC)
            created_madrid = created_utc.astimezone(madrid_tz)

            if users[user_id]["first_message_time"] is None:
                users[user_id]["first_message_time"] = created_madrid
            users[user_id]["last_message_time"] = created_madrid

            if time_range["start"] is None or created_madrid < time_range["start"]:
                time_range["start"] = created_madrid
            if time_range["end"] is None or created_madrid > time_range["end"]:
                time_range["end"] = created_madrid

        except Exception:
            continue

    # Build conversation threads
    threads, standalone_messages = build_conversation_threads(messages)

    # Format for AI analysis
    conversation_data = {
        "metadata": {
            "chat_id": chat_id,
            "export_date": export_time.strftime("%Y-%m-%d"),
            "total_messages": total_messages,
            "unique_participants": len(users),
            "time_range": {
                "start": time_range["start"].strftime("%Y-%m-%d %H:%M") if time_range["start"] else None,
                "end": time_range["end"].strftime("%Y-%m-%d %H:%M") if time_range["end"] else None,
                "duration_hours": (time_range["end"] - time_range["start"]).total_seconds() / 3600 if time_range["start"] and time_range["end"] else 0
            },
            "participants": [
                {
                    "name": user_data["name"],
                    "message_count": user_data["message_count"],
                    "participation_percentage": round((user_data["message_count"] / total_messages) * 100, 1)
                }
                for user_data in users.values()
            ]
        },

        "conversation_flow": [],

        "raw_chronological_transcript": "",

        "conversation_threads": []
    }

    # Build chronological conversation flow
    sorted_messages = sorted(messages, key=lambda x: x.get("telegram_message_id", 0))

    transcript_lines = []
    for msg in sorted_messages:
        try:
            created_utc = datetime.fromisoformat(msg["created_at"]).replace(tzinfo=pytz.UTC)
            created_madrid = created_utc.astimezone(madrid_tz)
            timestamp = created_madrid.strftime("%H:%M")

            username = msg.get("username") or msg.get("first_name") or str(msg.get("user_id"))
            text = msg.get("message_text", "")
            reply_to = msg.get("telegram_reply_to_message_id")

            # Add to conversation flow
            conversation_data["conversation_flow"].append({
                "timestamp": timestamp,
                "user": username,
                "message": text,
                "is_reply": bool(reply_to),
                "reply_to_id": reply_to
            })

            # Add to transcript
            if reply_to:
                transcript_lines.append(f"[{timestamp}] {username} (replying): {text}")
            else:
                transcript_lines.append(f"[{timestamp}] {username}: {text}")

        except Exception:
            continue

    conversation_data["raw_chronological_transcript"] = "\n".join(transcript_lines)

    # Build conversation threads for analysis
    for original_msg_id, thread_data in threads.items():
        original_msg = thread_data["original_message"]
        if original_msg:
            try:
                original_created = datetime.fromisoformat(original_msg["created_at"]).replace(tzinfo=pytz.UTC).astimezone(madrid_tz)
                original_user = original_msg.get("username") or original_msg.get("first_name") or str(original_msg.get("user_id"))

                thread_info = {
                    "thread_starter": {
                        "user": original_user,
                        "timestamp": original_created.strftime("%H:%M"),
                        "message": original_msg.get("message_text", "")
                    },
                    "replies": [],
                    "participants": set([original_user]),
                    "message_count": 1 + len(thread_data["replies"])
                }

                for reply in sorted(thread_data["replies"], key=lambda x: x.get("telegram_message_id", 0)):
                    try:
                        reply_created = datetime.fromisoformat(reply["created_at"]).replace(tzinfo=pytz.UTC).astimezone(madrid_tz)
                        reply_user = reply.get("username") or reply.get("first_name") or str(reply.get("user_id"))

                        thread_info["replies"].append({
                            "user": reply_user,
                            "timestamp": reply_created.strftime("%H:%M"),
                            "message": reply.get("message_text", "")
                        })
                        thread_info["participants"].add(reply_user)
                    except Exception:
                        continue

                thread_info["participants"] = list(thread_info["participants"])
                thread_info["unique_participants"] = len(thread_info["participants"])

                conversation_data["conversation_threads"].append(thread_info)

            except Exception:
                continue

    return conversation_data


@log_command()
@bot_started()
async def export_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export ALL available messages for this chat in an AI-optimized JSON format"""
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.debug(f"=== EXPORT CHAT COMMAND ===")
    logger.debug(f"Chat ID: {chat_id}, User ID: {user.id}")
    logger.debug(f"User: {user.first_name} {user.last_name} (@{user.username})")

    try:
        madrid_tz = pytz.timezone("Europe/Madrid")
        export_time = datetime.now(madrid_tz)

        logger.debug("Fetching ALL available messages for this chat...")

        # Get ALL messages for this chat (no date restrictions)
        # Use a high limit to get everything available
        messages = await db_service.get_recent_messages(chat_id, limit=10000)
        logger.debug(f"Total messages found: {len(messages)}")

        if not messages:
            logger.info(f"No messages found for export - Chat: {chat_id}")
            await update.message.reply_text(
                f"{ERROR_MESSAGES['NO_MESSAGES']}\n\n"
                f"🔍 *No hay mensajes en este chat para exportar.*",
                parse_mode="Markdown"
            )
            return

        logger.debug(f"Found {len(messages)} messages for export")
        logger.debug("Processing ALL messages for AI analysis format...")

        # Format messages for AI analysis
        conversation_data = format_for_ai_analysis(messages, chat_id, export_time)

        # Update metadata to reflect that this is a full export
        conversation_data["metadata"]["export_type"] = "full_chat_history"
        conversation_data["metadata"]["export_timestamp"] = export_time.strftime("%Y-%m-%d %H:%M")
        conversation_data["metadata"]["note"] = "Contains all available messages in database (auto-cleaned by scheduler)"

        logger.debug(f"Processed conversation data: {len(conversation_data['conversation_flow'])} messages, {len(conversation_data['conversation_threads'])} threads")

        # Create temporary file for export
        try:
            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json", encoding='utf-8') as tmp:
                json.dump(conversation_data, tmp, ensure_ascii=False, indent=2)
                tmp_path = tmp.name

            logger.debug(f"Temporary file created: {tmp_path}")

        except Exception as file_error:
            logger.error(f"Error creating temporary file: {file_error}", exc_info=True)
            await update.message.reply_text(ERROR_MESSAGES["FILE_CREATION_ERROR"])
            return

        # Send the document
        try:
            logger.debug("Sending document to user...")
            with open(tmp_path, "rb") as doc:
                # Generate filename with timestamp
                filename = f"chat_full_export_{export_time.strftime('%Y%m%d_%H%M')}.json"

                participants_count = conversation_data["metadata"]["unique_participants"]
                threads_count = len(conversation_data["conversation_threads"])
                duration = conversation_data["metadata"]["time_range"]["duration_hours"]

                caption = (
                    f"🧠 **Exportación completa del chat**\n"
                    f"• {len(messages)} mensajes totales\n"
                    f"• {participants_count} participantes\n"
                    f"• {threads_count} hilos de conversación\n"
                    f"• {duration:.1f} horas de conversación\n\n"
                    f"📋 *Todo el historial disponible - Optimizado para IA*"
                )

                await context.bot.send_document(
                    chat_id=chat_id,
                    document=doc,
                    filename=filename,
                    caption=caption,
                    parse_mode="Markdown"
                )

            logger.info(f"=== EXPORT CHAT COMMAND COMPLETED for user {user.id} in chat {chat_id} ===")
            logger.info(f"Exported {len(messages)} total messages in AI-optimized format")

        except Exception as send_error:
            logger.error(f"Error sending document: {send_error}", exc_info=True)
            await update.message.reply_text(ERROR_MESSAGES["SEND_ERROR"])
            return
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    logger.debug(f"Temporary file cleaned up: {tmp_path}")
            except Exception as cleanup_error:
                logger.warning(f"Error cleaning up temporary file: {cleanup_error}")

    except Exception as e:
        logger.error(f"=== EXPORT CHAT COMMAND FAILED ===")
        logger.error(f"Error in export_chat_command for user {user.id}: {e}", exc_info=True)
        try:
            await update.message.reply_text(ERROR_MESSAGES["EXPORT_ERROR"])
        except Exception as reply_error:
            logger.error(f"Failed to send error message to user: {reply_error}")
