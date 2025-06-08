from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.services import db_service
from bot.utils.constants import LABELS, get_label, get_button_label
from bot.utils.decorators import log_command
from bot.utils.logger import logger

logger = logger.get_logger(__name__)


@log_command()
async def configure_summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the summary configuration menu with current settings."""
    try:
        chat_id = update.effective_chat.id

        # Get current config from database
        config = await db_service.get_chat_summary_config(chat_id)
        language = config.get('language', 'es')

        # Create main menu message
        message_text = get_label('title_main', language) + "\n\n"

        # Add current settings
        message_text += f"🧠 {get_label('tone_label', language)}: {get_button_label('tone', config['tone'], language)}\n"
        message_text += f"📏 {get_label('length_label', language)}: {get_button_label('length', config['length'], language)}\n"
        message_text += f"🌐 {get_label('language_label', language)}: {get_button_label('language', config['language'], language)}\n"
        message_text += f"👥 {get_label('names_label', language)}: {get_button_label('include_names', 'true' if config['include_names'] else 'false', language)}\n"
        message_text += f"⏰ {get_label('hour_label', language)}: {get_button_label('daily_summary_hour', config['daily_summary_hour'], language)}\n"

        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton(get_label('tone_button', language), callback_data="cfg|tone|open"),
                InlineKeyboardButton(get_label('length_button', language), callback_data="cfg|length|open"),
                InlineKeyboardButton(get_label('language_button', language), callback_data="cfg|language|open")
            ],
            [
                InlineKeyboardButton(get_label('names_button', language), callback_data="cfg|include_names|open"),
                InlineKeyboardButton(get_label('hour_button', language), callback_data="cfg|daily_summary_hour|open")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Check if this is a new message or an edit from callback
        if context.user_data.get('config_message_id'):
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=context.user_data['config_message_id'],
                    text=message_text,
                    reply_markup=reply_markup
                )
                logger.info(f"Updated configuration message for chat {chat_id}")
            except Exception as e:
                logger.warning(f"Failed to edit message, sending new one: {e}")
                # If edit fails (message too old), send new message
                message = await update.effective_message.reply_text(
                    text=message_text,
                    reply_markup=reply_markup
                )
                context.user_data['config_message_id'] = message.message_id
                logger.info(f"Sent new configuration message for chat {chat_id}")
        else:
            # Send as new message
            message = await update.effective_message.reply_text(
                text=message_text,
                reply_markup=reply_markup
            )
            context.user_data['config_message_id'] = message.message_id
            logger.info(f"Sent initial configuration message for chat {chat_id}")

    except Exception as e:
        logger.error(f"Error in configure_summary_command: {e}", exc_info=True)
        await update.effective_message.reply_text(
            "❌ Error al mostrar la configuración. Por favor, inténtalo de nuevo más tarde."
        )
