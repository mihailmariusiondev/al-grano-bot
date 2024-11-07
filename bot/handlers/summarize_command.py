import random
from telegram.ext import CallbackContext
from telegram import Update
from bot.utils.decorators import premium_only, log_command, bot_started
from bot.utils.format_utils import format_recent_messages
from bot.utils.logger import logger
from bot.services.database_service import db_service

WAIT_FOR_SUMMARY_REPLIES = [
    'Espérate un segundo, crack, que te lo resumo en un plis. No te me impacientes, coño.',
    'Un segundito, cabronazo, que te hago el resumen de puta madre. Que no cunda el pánico.',
    'Tranqui, figura, que esto está chupao. Te lo sintetizo en un periquete.',
    'No me metas presión, puto amo. Te juro que te lo resumo de la hostia.',
    'Tú relájate, machote, que yo me encargo de esta mierda. Te va a flipar el resumen.',
    'Al loro, crack, que te voy a hacer un resumen que te cagas. Dame un minutito.',
    'Joder, qué prisas tienes, cabronazo. Que ya te lo resumo, coño, no me agobies.',
    'No te me cagues encima, puto amo. Te voy a hacer un resumen de la hostia en nada.',
    'Me cago en la puta, tío, déjame currarme el resumen. Te va a dejar flipando.',
    'No te sulfures, gilipollas, que ya te preparo el resumen. Te va a encantar, hostias.',
    'Espérate un poquito, tontaina, que te resumo esta mierda pero ya. Ni te vas a enterar de lo rápido que va a ser.',
    'Quieto, parao, figura. Te voy a hacer un resumen que te va a dejar con el culo torcío.',
    'No me toques los cojones, que estoy resumiendo a tope. En un momento te lo suelto.',
    'Relaja la raja, cabronazo, que te estoy haciendo un resumen de la hostia. Tú espera y flipa.',
    'Un segundito, puto amo, que estoy en modo resumen. Te va a encantar esta mierda.',
    'No te me aceleres, gilipollas. Que te voy a hacer un resumen que te cagas. Espérate un poco.',
    'Tranquilidad, máquina, que te lo resumo en un pis pas. Tú dame un segundo y alucina.',
    'Eh, tontaina, que estoy resumiendo a toda hostia. No me metas presión, coño.',
    'Que te calles un momento, cabronazo. Te voy a hacer un resumen que te va a dejar loco.',
    'A ver, puto amo, que te lo resumo en nada. Tú quieto y espérate un segundo.',
    'No te me pongas nervioso, figura. Te estoy haciendo un resumen de la hostia. Ya verás qué flipada.',
    'Eh, gilipollas, que estoy concentrado resumiendo. Dame un puto minuto y te lo suelto.',
    'Hostia, tío, que estoy a tope con el resumen. Tú tranqui, que en nada te lo mando.',
    'Espérate un momencito, crack, que te voy a dejar flipando con este resumen.',
    'No me estreses, cabronazo, que ya casi tengo el resumen listo. Te va a encantar, joder.',
    'Un segundito más, puto amo, que esto va a ser un resumen de la hostia. Tú confía en mí.',
    'Me cago en la leche, figura, que estoy resumiendo a toda mecha. No seas impaciente, coño.',
    'Que te esperes, cojones, que te voy a hacer un resumen que te va a dejar con la boca abierta.',
    'Tranqui, gilipollas, que ya casi lo tengo. Este resumen te va a hacer flipar en colores.',
    'Joder, tío, que no me metas presión. Que te lo resumo de puta madre en un momento.'
]

ERROR_MESSAGES = {
    'NOT_ENOUGH_MESSAGES': 'No hay suficientes mensajes para resumir. O me das 5 mensajes o te mando a la mierda',
    'ERROR_SUMMARIZING': 'Error al resumir los mensajes. Ya la hemos liao... ',
    'INVALID_YOUTUBE_URL': 'URL de YouTube inválida. Eres tonto o qué?..',
    'NOT_REPLYING_TO_MESSAGE': 'No estás respondiendo a ningún mensaje. No me toques los co',
    'ERROR_TRANSCRIPT_DISABLED': 'Transcripción deshabilitada para este vídeo. No me presiones tronco',
    'ERROR_CANNOT_SUMMARIZE_ARTICLE': 'Pues va a ser que el artículo este no tiene chicha que resumir. Será más soso que un bocata de arena o está escrito en jeroglíficos. ¡Ni el puto Indiana Jones sacaría algo en claro, tronco!',
    'ERROR_EMPTY_SUMMARY': 'Error: El resumen está vacío. Parece que no había nada importante que decir, joder.',
    'ERROR_INVALID_SUMMARY': 'Error: El resumen es inválido. Puede que haya entendido algo mal, coño.',
    'ERROR_UNKNOWN': 'Error: Algo ha ido mal al resumir. No tengo ni puta idea de qué ha pasado.',
    'ERROR_DOWNLOADING_AUDIO': 'Error: Me he hecho la picha un lío descargando el audio. Prueba otra vez, figura.',
    'ERROR_PROCESSING_AUDIO': 'Error: Me he quedado pillado procesando el audio. Dale otra vez, campeón.'
}

logger = logger.get_logger(__name__)

@premium_only()
@log_command()
@bot_started()
async def summarize_command(update: Update, context: CallbackContext):
    logger.debug('Comando /summarize iniciado')
    try:
        chat_id = update.effective_chat.id
        if not chat_id:
            return

        wait_message_text = random.choice(WAIT_FOR_SUMMARY_REPLIES)
        wait_message = await update.message.reply_text(wait_message_text)

        current_time = int(update.message.date.timestamp() * 1000)
        await db_service.update_chat_state(chat_id, {'last_command_usage': current_time})
        logger.info(f"Tiempo de último uso del comando actualizado para chat_id: {chat_id}")

        summary = ''
        original_message = None

        if not update.message.reply_to_message:
            logger.debug('No se encontró respuesta. Resumiendo mensajes recientes')
            summary = summarize_recent_chat_messages(chat_id, update, context)
        else:
            replied_message = update.message.reply_to_message
            if replied_message.text:
                summary = summarize_replied_message(replied_message.text)
                original_message = replied_message
            elif replied_message.voice:
                summary = summarize_audio_message(update, context, replied_message.voice.file_id)
                original_message = replied_message
            else:
                logger.debug('Respuesta inválida')
                update.message.reply_text('Respuesta inválida. Por favor, responde a un mensaje de texto, un enlace válido de YouTube o un mensaje de voz.')
                return

        logger.debug(f"Resumen: {summary}")

        context.bot.delete_message(chat_id=wait_message.chat_id, message_id=wait_message.message_id)

        if original_message:
            update.message.reply_text(summary, reply_to_message_id=original_message.message_id)
        else:
            update.message.reply_text(summary)

    except Exception as e:
        logger.error(f"Error en summarize_command: {e}")
        raise e

async def summarize_recent_chat_messages(chat_id, update, context):
    logger.debug('Resumiendo los últimos 300 mensajes.')
    recent_messages = await db_service.get_recent_messages(chat_id, 300)
    logger.debug(f"Cantidad de mensajes recientes: {len(recent_messages)}")
    if len(recent_messages) < 5:
        logger.debug('No hay suficientes mensajes.')
        await update.message.reply_text(ERROR_MESSAGES['NOT_ENOUGH_MESSAGES'])
        return ''
    formatted_messages = format_recent_messages(recent_messages)
    summary = get_summary_chat_content(formatted_messages, bot_config['LANGUAGE'])
    return summary

def summarize_replied_message(replied_text):
    logger.debug('Resumiendo mensaje de texto respondido.')
    summary = get_summary_general_content(replied_text, bot_config['LANGUAGE'])
    return summary

def summarize_audio_message(update, context, voice_file_id):
    try:
        file = context.bot.get_file(voice_file_id)
        input_file_path = download_audio_file(file.file_path, voice_file_id)
        output_file_path = process_audio_file(input_file_path, voice_file_id)
        transcript_text = transcribe_audio_file(output_file_path)
        logger.debug(f"Transcripción: {transcript_text}")
        summary_text = get_summary_general_content(transcript_text, bot_config['LANGUAGE'])
        delete_audio_files([input_file_path, output_file_path])
        return summary_text
    except Exception as e:
        logger.error(f"Error en summarize_audio_message: {e}")
        return ERROR_MESSAGES['ERROR_SUMMARIZING']
