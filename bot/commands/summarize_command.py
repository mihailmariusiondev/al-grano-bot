from telegram.ext import CallbackContext
from telegram import Update
from utils.decorators import admin_command, log_command, bot_started, rate_limit
from utils.format_utils import format_recent_messages
from utils.logger import logger
from services import db_service

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

@admin_command()
@log_command()
@bot_started()
@rate_limit(10)
async def summarize_command(update: Update, context: CallbackContext):
    # TODO: Implement summarize command for all:
    # "chat", "youtube", "telegram_video", "voice_message", "audio_file", "quoted_message", "web_article"
    pass
