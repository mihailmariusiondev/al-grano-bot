from telegram.ext import CallbackContext
from telegram import Update
from utils.decorators import admin_command, log_command, bot_started, rate_limit_by_chat
from utils.format_utils import format_recent_messages, send_long_message
from utils.logger import logger
from utils.get_message_type import get_message_type
from utils.constants import YOUTUBE_REGEX, ARTICLE_URL_REGEX
from services import db_service, openai_service
from handlers.youtube_handler import youtube_handler
from handlers.video_handler import video_handler
from handlers.audio_handler import audio_handler
from handlers.article_handler import article_handler
from handlers.document_handler import document_handler
import random
import asyncio

WAIT_FOR_SUMMARY_REPLIES = [
    "Espérate un segundo, crack, que te lo resumo en un plis. No te me impacientes, coño.",
    "Un segundito, cabronazo, que te hago el resumen de puta madre. Que no cunda el pánico.",
    "Tranqui, figura, que esto está chupao. Te lo sintetizo en un periquete.",
    "No me metas presión, puto amo. Te juro que te lo resumo de la hostia.",
    "Tú relájate, machote, que yo me encargo de esta mierda. Te va a flipar el resumen.",
    "Al loro, crack, que te voy a hacer un resumen que te cagas. Dame un minutito.",
    "Joder, qué prisas tienes, cabronazo. Que ya te lo resumo, coño, no me agobies.",
    "No te me cagues encima, puto amo. Te voy a hacer un resumen de la hostia en nada.",
    "Me cago en la puta, tío, déjame currarme el resumen. Te va a dejar flipando.",
    "No te sulfures, gilipollas, que ya te preparo el resumen. Te va a encantar, hostias.",
    "Espérate un poquito, tontaina, que te resumo esta mierda pero ya. Ni te vas a enterar de lo rápido que va a ser.",
    "Quieto, parao, figura. Te voy a hacer un resumen que te va a dejar con el culo torcío.",
    "No me toques los cojones, que estoy resumiendo a tope. En un momento te lo suelto.",
    "Relaja la raja, cabronazo, que te estoy haciendo un resumen de la hostia. Tú espera y flipa.",
    "Un segundito, puto amo, que estoy en modo resumen. Te va a encantar esta mierda.",
    "No te me aceleres, gilipollas. Que te voy a hacer un resumen que te cagas. Espérate un poco.",
    "Tranquilidad, máquina, que te lo resumo en un pis pas. Tú dame un segundo y alucina.",
    "Eh, tontaina, que estoy resumiendo a toda hostia. No me metas presión, coño.",
    "Que te calles un momento, cabronazo. Te voy a hacer un resumen que te va a dejar loco.",
    "A ver, puto amo, que te lo resumo en nada. Tú quieto y espérate un segundo.",
    "No te me pongas nervioso, figura. Te estoy haciendo un resumen de la hostia. Ya verás qué flipada.",
    "Eh, gilipollas, que estoy concentrado resumiendo. Dame un puto minuto y te lo suelto.",
    "Hostia, tío, que estoy a tope con el resumen. Tú tranqui, que en nada te lo mando.",
    "Espérate un momencito, crack, que te voy a dejar flipando con este resumen.",
    "No me estreses, cabronazo, que ya casi tengo el resumen listo. Te va a encantar, joder.",
    "Un segundito más, puto amo, que esto va a ser un resumen de la hostia. Tú confía en mí.",
    "Me cago en la leche, figura, que estoy resumiendo a toda mecha. No seas impaciente, coño.",
    "Que te esperes, cojones, que te voy a hacer un resumen que te va a dejar con la boca abierta.",
    "Tranqui, gilipollas, que ya casi lo tengo. Este resumen te va a hacer flipar en colores.",
    "Joder, tío, que no me metas presión. Que te lo resumo de puta madre en un momento.",
]

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
@log_command()
@bot_started()
@rate_limit_by_chat(10)
async def summarize_command(update: Update, context: CallbackContext):
    """Handle the /summarize command for different types of content"""
    try:
        # Initial waiting message
        wait_message = await update.message.reply_text(
            random.choice(WAIT_FOR_SUMMARY_REPLIES)
        )

        # Case 1: No reply - summarize recent messages
        if not update.message.reply_to_message:
            await update_progress(wait_message, PROGRESS_MESSAGES["FETCHING_MESSAGES"])

            recent_messages = await db_service.get_recent_messages(
                update.effective_chat.id, 300
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
                await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                await update_progress(wait_message, PROGRESS_MESSAGES["TRANSCRIBING"])
                content = await audio_handler(reply_msg, context)
                summary_type = (
                    "voice_message" if message_type == "voice" else "audio_file"
                )

            case "video" | "video_note":
                await update_progress(wait_message, PROGRESS_MESSAGES["DOWNLOADING"])
                await update_progress(wait_message, PROGRESS_MESSAGES["PROCESSING"])
                content = await video_handler(reply_msg, context)
                summary_type = "telegram_video"

            case "document":
                await update_progress(wait_message, PROGRESS_MESSAGES["ANALYZING"])
                mime_type = reply_msg.document.mime_type
                if mime_type:
                    if mime_type.startswith("audio/"):
                        await update_progress(
                            wait_message, PROGRESS_MESSAGES["TRANSCRIBING"]
                        )
                        content = await audio_handler(reply_msg, context)
                        summary_type = "audio_file"
                    elif mime_type.startswith("video/"):
                        await update_progress(
                            wait_message, PROGRESS_MESSAGES["PROCESSING"]
                        )
                        content = await video_handler(reply_msg, context)
                        summary_type = "telegram_video"
                    elif mime_type in ["text/plain", "application/pdf"]:
                        await update_progress(
                            wait_message, PROGRESS_MESSAGES["PROCESSING"]
                        )
                        content = await document_handler(reply_msg, context)
                        summary_type = "document"

            case "photo":
                if reply_msg.caption:
                    content = reply_msg.caption
                    summary_type = "quoted_message"
                else:
                    await wait_message.edit_text(ERROR_MESSAGES["ERROR_NO_CAPTION"])
                    return

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
        logger.error(f"Error in summarize_command: {e}", exc_info=True)
        await update.message.reply_text(ERROR_MESSAGES["ERROR_SUMMARIZING"])
        raise
