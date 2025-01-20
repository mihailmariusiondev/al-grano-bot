from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command, bot_started, admin_command
from bot.utils.logger import logger
from bot.services.database_service import db_service

logger = logger.get_logger(__name__)


@admin_command()
@log_command()
@bot_started()
async def toggle_summary_type_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Toggle between long/short summary formats"""
    try:
        chat_id = update.effective_chat.id
        chat_state = await db_service.get_chat_state(chat_id)
        current_type = chat_state.get("summary_type", "long")
        new_type = "short" if current_type == "long" else "long"

        await db_service.update_chat_state(chat_id, {"summary_type": new_type})

        await update.message.reply_text(
            f"✅ Formato de resumen cambiado a {'corto' if new_type == 'short' else 'largo'}.\n"
            f"Los próximos resúmenes serán más {'concisos' if new_type == 'short' else 'detallados'}."
        )
    except Exception as e:
        logger.error(f"Error in toggle_summary_type_command: {e}", exc_info=True)
        await update.message.reply_text("❌ Error al cambiar el formato de resumen.")
        raise
