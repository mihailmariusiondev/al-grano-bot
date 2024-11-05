from telegram import Update
from telegram.ext import ContextTypes
from ..utils.decorators import admin_command
from ..utils.logger import logger
from ..services.database_service import db_service

logger = logger.get_logger("handlers.admin")

@admin_command
async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /stats command - show bot statistics"""
    try:
        users = await db_service.fetch_one("SELECT COUNT(*) as count FROM users")
        stats_text = (
            "📊 Estadísticas del Bot:\n"
            f"- Usuarios totales: {users['count']}\n"
        )
        await update.message.reply_text(stats_text)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await update.message.reply_text("Error al obtener estadísticas.")

@admin_command
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /broadcast command - send message to all users"""
    if not context.args:
        await update.message.reply_text("Uso: /broadcast <mensaje>")
        return

    message = " ".join(context.args)
    try:
        users = await db_service.fetch_all("SELECT user_id FROM users")
        sent_count = 0
        for user in users:
            try:
                await context.bot.send_message(user['user_id'], message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Error sending broadcast to {user['user_id']}: {e}")

        await update.message.reply_text(f"Mensaje enviado a {sent_count} usuarios.")
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        await update.message.reply_text("Error al enviar broadcast.")
