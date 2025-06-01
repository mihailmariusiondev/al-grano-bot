# bot/commands/help_command.py

from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.logger import logger
from bot.utils.decorators import log_command, bot_started
from bot.services.database_service import db_service
from bot.utils.constants import (
    COOLDOWN_TEXT_SIMPLE_SECONDS,
    COOLDOWN_ADVANCED_SECONDS,
    DAILY_LIMIT_ADVANCED_OPS
)
import asyncio

logger = logger.get_logger(__name__)

cooldown_simple_minutes = COOLDOWN_TEXT_SIMPLE_SECONDS // 60
cooldown_advanced_minutes = COOLDOWN_ADVANCED_SECONDS // 60

HELP_MESSAGE = (
    "👋 **¡Eh, tú! Bienvenido al Bot de Resúmenes Al-Grano, el puto amo resumiendo mierdas.** 👋\n\n"
    "Este bot está aquí para que dejes de perder el tiempo leyendo tochos. Yo te lo resumo y te vas de cañas. Aquí te va el rollo, para que te enteres:\n\n"
    "🔹 **Comandos para que no te ahogues en mierda:**\n"
    "• `/start` - Despierta a esta bestia y dile que curre en este chat. ¡YA!\n"
    "• `/help` - Si eres tan corto que necesitas ayuda, aquí tienes esta parrafada. ¡Léetela!\n"
    "• `/summarize` - El puto amo de los comandos. Te resume lo que sea. ¡Pídele y calla!\n"
    "• `/configurar_resumen` - Personaliza el tono, longitud, idioma y programa resúmenes diarios. ¡Ponlo a tu gusto!\n\n"
    "🔹 **Cómo usar `/summarize` sin parecer un paquete:**\n"
    "• **Resumir el chat como un vago (Operación Simple):**\n"
    "  Tira un `/summarize` y déjalo que se curre los últimos mensajes del chat (hasta 300). ¡Menos leer para ti, fenómeno!\n\n"
    "• **Resumir UN puto mensaje (Simple o Avanzado, según le dé):**\n"
    "  Responde a un mensaje con `/summarize`. No es física cuántica, ¿verdad? El bot se encarga, tú solo espera.\n\n"
    "🔹 **Qué mierdas resume este cacharro (y ojo con los límites, que no soy tu esclavo):**\n\n"
    "  **Operaciones SIMPLES (para gente con prisa y poco presupuesto):**\n"
    "  ⏱️ **¡Quieto parao 2 MINUTOS!** No me seas ansias entre usos.\n"
    "  • **Mensajes de Texto:** Te resumo la cháchara del chat o ese mensaje de texto que te da pereza leer.\n"
    "  • **Enlaces de YouTube:** Me chivo los subtítulos (si los hay, claro) y te planto un resumen. ¡De nada!\n"
    "  • **Artículos Web:** Pásame el link y te saco el jugo, para que no te tragues el tostón entero.\n\n"
    "  **Operaciones AVANZADAS (estas me cuestan la pasta y el curro, así que ojito):**\n"
    "  ⏱️ **¡A esperar 10 MINUTAZOS, figura!** Que esto no es gratis.\n"
    "  📈 **SOLO 5 de estas al día, ¿eh?** Si no eres admin, claro. Los jefes, barra libre.\n"
    "  • **Archivos de Audio y Mensajes de Voz:** Los transcribo y te los resumo. Me entero de todo, ¡cabrón!\n"
    "  • **Videos y Notas de Video (archivos):** Les saco el audio, lo transcribo y te lo resumo. ¡Un currazo que te cagas!\n"
    "  • **Documentos (PDF, DOCX, TXT):** Les echo un ojo, saco el texto y te lo resumo. Si es un ladrillo, tardaré un poco, pero no me rajo.\n\n"
    "🔹 **Avisos para navegantes (¡más te vale leer esto!):**\n"
    "• **Si eres un tieso (usuario gratuito):** Para que no me revientes el chiringuito, te pongo límites. Los cooldowns son para que respires entre comando y comando. Y las operaciones avanzadas (transcribir audios/vídeos, documentos tochos... esas que me hacen sudar tinta y gastar billetes) tienen un límite diario. Si eres admin, te puedes pasar el día dándome por culo, me da igual.\n"
    "• **Archivos, el tamaño SÍ importa:** Máximo 20MB. Si me pasas algo más gordo, te lo comes con patatas. No soy un disco duro con patas.\n\n"
    "🔹 **Si te mola cómo curro y quieres que siga dando guerra (o invitarme a una birra):**\n"
    "Este tinglado lo montó [@Arkantos2374](https://t.me/Arkantos2374), que se ha dejado las pestañas en ello. Si quieres que no me muera de hambre y que el bot siga rulando, suéltale algo por [PayPal](https://paypal.me/mariusmihailion). ¡Se agradece, fiera!\n\n"
    "🚀 **¡Venga, a darle al `/summarize` y déjate de hostias!** 🚀"
)

@log_command()
@bot_started()
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error en help_handler: {e}")
        await update.message.reply_text(
            "¡Hostia puta! Algo ha petado al intentar mostrarte la ayuda. Inténtalo otra vez, anda."
        )
        raise e
