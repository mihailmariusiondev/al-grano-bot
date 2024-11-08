from telegram import Update
from telegram.ext import CallbackContext
from utils.decorators import admin_command, log_command, rate_limit_by_chat
from services import db_service
from utils.logger import logger


@admin_command()
@log_command()
@rate_limit_by_chat(30)
async def stats_handler(update: Update, context: CallbackContext) -> None:
    """Handle stats command to show usage statistics"""
    try:
        user_id = update.effective_user.id
        stats = await db_service.get_user_usage_stats(user_id)

        if not stats:
            await update.message.reply_text("No hay estadísticas de uso disponibles.")
            return

        message = "*Estadísticas de uso:*\n\n"
        for stat in stats:
            message += f"• {stat['command']}: {stat['usage_count']} usos\n"
            message += f"  Último uso: {stat['last_used']}\n\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in stats handler: {e}")
        await update.message.reply_text("❌ Error al obtener las estadísticas")
        raise
