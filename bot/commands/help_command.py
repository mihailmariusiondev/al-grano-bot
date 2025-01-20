# bot/commands/help_command.py

from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.logger import logger
from bot.utils.decorators import log_command, bot_started
from bot.services.database_service import db_service
from telegram.ext import ContextTypes
import asyncio

logger = logger.get_logger(__name__)

HELP_MESSAGE = (
    "👋 **Bienvenido al Bot de Resúmenes Al-Grano** 👋\n\n"
    "Este bot está diseñado para ayudarte a resumir contenido de manera rápida y eficiente. A continuación, se detallan todos los comandos y funcionalidades disponibles:\n\n"
    "🔹 **Comandos Disponibles:**\n"
    "• `/start` - Inicia el bot y configura el estado inicial en el chat.\n"
    "• `/help` - Muestra esta guía de ayuda detallada.\n"
    "• `/about` - Proporciona información sobre el creador y el propósito del bot.\n"
    "• `/summarize` - Genera resúmenes de mensajes o contenido específico.\n"
    "• `/toggle_daily_summary` - Activa o desactiva el resumen diario automático del chat.\n"
    "• `/toggle_summary_type` - Alterna entre resúmenes largos detallados y cortos concisos.\n\n"
    "🔹 **Cómo Usar `/summarize`:**\n"
    "• **Resumir los últimos mensajes del chat:**\n"
    "  Simplemente envía `/summarize` sin responder a ningún mensaje. El bot resumirá los últimos 300 mensajes del chat para que no se te escape nada importante.\n\n"
    "• **Resumir un mensaje específico:**\n"
    "  Responde a un mensaje con `/summarize` y el bot generará un resumen del contenido de ese mensaje. Esto incluye texto, enlaces de YouTube, documentos, audio, video, encuestas, etc.\n\n"
    "• **Resumir un video de YouTube:**\n"
    "  Si respondes a un mensaje que contiene un enlace de YouTube con `/summarize`, el bot extraerá y resumirá los subtítulos del video para proporcionarte una visión general del contenido.\n\n"
    "🔹 **Tipos de Contenido que el Bot Puede Resumir:**\n"
    "• **Mensajes de Texto:** Resumen de conversaciones recientes o mensajes específicos.\n"
    "• **Enlaces de YouTube:** Resumen de videos mediante subtítulos disponibles.\n"
    "• **Documentos:** Resumen de archivos como PDF, DOCX y TXT.\n"
    "• **Archivos de Audio y Voz:** Transcripción y resumen de mensajes de voz o archivos de audio.\n"
    "• **Videos y Notas de Video:** Extracción de audio, transcripción y resumen de contenido de video.\n"
    "• **Encuestas:** Resumen de preguntas y opciones de encuestas enviadas en el chat.\n\n"
    "🔹 **Características Adicionales:**\n"
    "• **Almacenamiento de Mensajes:** Todos los mensajes enviados en el chat se almacenan en la base de datos para facilitar la generación de resúmenes precisos.\n"
    "• **Usuarios Premium:** Acceso exclusivo a funcionalidades avanzadas como resúmenes más detallados y mayor capacidad de procesamiento.\n"
    "• **Administradores:** Comandos especiales y permisos adicionales para usuarios administradores.\n\n"
    "🔹 **Notas Importantes:**\n"
    "• **Seguridad y Privacidad:** El bot maneja información sensible. Asegúrate de que solo usuarios autorizados tengan acceso a comandos privilegiados.\n"
    "• **Limitaciones:** El tamaño máximo de archivos para procesamiento es de 20 MB. Asegúrate de que los archivos que envías cumplan con este límite.\n\n"
    "🔹 **Soporte y Donaciones:**\n"
    "Este bot ha sido creado por [@Arkantos2374](https://t.me/Arkantos2374) con mucho esfuerzo. Si deseas apoyar el desarrollo y mantenimiento del bot, puedes realizar una donación vía [PayPal](https://paypal.me/mariusmihailion). ¡Gracias por tu apoyo!\n\n"
    "🚀 **¡Vamos a darle caña a esto y a resumir al grano!** 🚀"
)


@log_command()
@bot_started()
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error en help_handler: {e}")
        await update.message.reply_text(
            "Hubo un error al procesar tu solicitud de ayuda."
        )
        raise e
