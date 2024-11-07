from telegram import Update
from telegram.ext import ContextTypes
from ..utils.logger import logger
from ..config import config

logger = logger.get_logger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    is_admin = update.effective_user.id in (config.ADMIN_USERS or [])

    help_text = (
        "📚 **Ayuda de Al Grano Bot** 📚\n\n"
        "**Comandos Disponibles:**\n"
        "/summarize - Genera un resumen de los últimos mensajes o del contenido específico al que respondas.\n"
        "/help - Muestra esta ayuda con más detalles sobre cómo usar el bot.\n\n"
        "**Cómo Usar:**\n"
        "1. **Resumen de Chat:** Envía `/summarize` sin responder a ningún mensaje para resumir los últimos 300 mensajes del chat.\n"
        "2. **Resumen de Mensaje Específico:** Responde a un mensaje con `/summarize` para obtener un resumen de ese contenido.\n"
        "3. **Resumen de Video de YouTube:** Responde a un mensaje con un enlace de YouTube y envía `/summarize` para obtener un resumen del video.\n"
        "4. **Resumen de Artículo Web:** Responde a un mensaje con una URL de un artículo y envía `/summarize` para obtener un resumen del artículo.\n"
        "5. **Resumen de Mensaje de Voz:** Responde a un mensaje de voz con `/summarize` para obtener una transcripción y resumen del audio.\n\n"
        "🔧 **Configuración:**\n"
        "Actualmente, todas las funcionalidades están configuradas para operar en español de España y utilizan exclusivamente la API de OpenAI para la generación de resúmenes.\n\n"
        "🚀 **¡Eso es todo!** Si tienes alguna pregunta adicional o encuentras algún problema, no dudes en contactarme."
    )

    if is_admin:
        help_text += (
            "\n\n**Comandos de administrador:**\n"
            "/stats - Ver estadísticas del bot\n"
            "/broadcast - Enviar mensaje a todos los usuarios"
        )

    await update.message.reply_text(help_text, parse_mode="Markdown")
    logger.debug(f"Help response sent to user {update.effective_user.id}")
