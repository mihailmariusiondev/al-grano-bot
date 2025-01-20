from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command, bot_started, admin_command
from bot.utils.logger import logger
from bot.services.database_service import db_service

logger = logger.get_logger(__name__)


@admin_command()
@log_command()
@bot_started()
async def toggle_daily_summary_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Toggle daily summary generation for a chat"""
    try:
        chat_id = update.effective_chat.id

        # Get current chat state
        chat_state = await db_service.get_chat_state(chat_id)

        # Get current daily summary state, default to False if not set
        current_state = chat_state.get("daily_summary_enabled", False)

        # Toggle the state
        new_state = not current_state

        # Update the state in database
        await db_service.update_chat_state(
            chat_id, {"daily_summary_enabled": new_state}
        )

        # Send confirmation message
        status = "activado" if new_state else "desactivado"
        await update.message.reply_text(
            f"✅ El resumen diario ha sido {status} para este chat.\n"
            f"Se generará {'cada día a las 3 AM (hora española)' if new_state else 'cuando lo vuelvas a activar'}."
        )

    except Exception as e:
        logger.error(f"Error in toggle_daily_summary_command: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Ocurrió un error al cambiar el estado del resumen diario."
        )
        raise
