from telegram import Update
from telegram.ext import CallbackContext
from utils.decorators import admin_command, log_command, rate_limit_by_chat
from services import db_service
from utils.logger import logger

HELP_MESSAGE = """
📝 *Configuración del Chat*

Comandos disponibles:
/config - Muestra la configuración actual
/config set <clave> <valor> - Actualiza una configuración

Configuraciones disponibles:
• max_summary_length - Longitud máxima del resumen (default: 2000)
• language - Idioma del resumen (default: es)
• auto_summarize - Resumen automático (true/false)
• auto_summarize_threshold - Mensajes para resumen auto (default: 50)
• cleanup_days - Días a mantener mensajes (default: 30)
• cleanup_min_messages - Mínimo de mensajes a mantener (default: 1000)
• cleanup_threshold - Límite para limpieza (default: 10000)
• is_bot_started - Estado de inicio del bot (true/false)
"""


@admin_command()
@log_command()
@rate_limit_by_chat(5)
async def config_handler(update: Update, context: CallbackContext) -> None:
    """Handle chat configuration commands"""
    try:
        chat_id = update.effective_chat.id
        args = context.args

        # Show current config if no args
        if not args:
            config = await db_service.get_chat_config(chat_id)
            message = "*Configuración actual:*\n"
            for key, value in config.items():
                if key not in ["chat_id", "created_at", "updated_at"]:
                    message += f"• {key}: `{value}`\n"
            await update.message.reply_text(message, parse_mode="Markdown")
            return

        # Show help if requested
        if args[0] == "help":
            await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")
            return

        # Handle configuration updates
        if args[0] == "set" and len(args) >= 3:
            key = args[1]
            value = args[2]

            # Convert string value to appropriate type
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)

            # Update config
            updated_config = await db_service.update_chat_config(chat_id, {key: value})

            if updated_config:
                await update.message.reply_text(
                    f"✅ Configuración actualizada: {key} = `{value}`",
                    parse_mode="Markdown",
                )
            else:
                await update.message.reply_text("❌ Error: Configuración inválida")
        else:
            await update.message.reply_text(
                "❌ Comando inválido. Usa /config help para ver las opciones disponibles."
            )

    except Exception as e:
        logger.error(f"Error in config handler: {e}")
        await update.message.reply_text("❌ Error al procesar la configuración")
        raise
