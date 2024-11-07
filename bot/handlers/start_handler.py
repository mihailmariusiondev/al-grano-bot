from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from bot.services import db_service
from bot.utils.decorators import log_command, rate_limit
from bot.utils.logger import logger

logger = logger.get_logger(__name__)

START_MESSAGE = (
        "¡Eeeeeeh, figura! Soy el puto amo resumiendo mierdas. Si quieres flipar con lo que sé hacer, presta atención:\n"
        "- Escribe /summarize sin responder a ningún mensaje y te resumo los últimos 300 mensajes de este puto chat. Así no se te escapa ni una, crack.\n"
        "- Responde a un mensaje con /summarize y te lo resumo en un plis, sin mariconadas. Voy al grano, como tiene que ser.\n"
        "- Responde a un mensaje con un enlace de YouTube y escribe /summarize. Te hago un resumen del puto video que flipas. Soy la hostia, ¿eh?\n"
        "Así que ya sabes, si no quieres andar perdido como un gilipollas, escríbeme /summarize y te pongo al día en un momento.\n"
        "Si no te enteras de una mierda, escribe /help y te lo explico, tontaina. ¡Vamos a darle caña a esto, coño!\n"
        "Este pedazo de bot lo ha creado el crack de @Arkantos2374. El muy cabrón se pulsa todos los costes de hosting y de las APIs de su puto bolsillo, así que si te molo y quieres que siga currando como un hijo de puta, cualquier donativo me vendría de puta madre. Si te sale de los cojones, puedes donar en paypal.me/mariusmihailion. ¡Gracias, puto amo!"
    )

@rate_limit(60)
@log_command()
async def start_handler(update: Update, context: CallbackContext):
    try:
        chat_id = update.effective_chat.id
        await db_service.update_chat_state(chat_id, {'is_bot_started': True})
        await update.message.reply_text(START_MESSAGE, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error en start_handler: {e}")
        raise e
