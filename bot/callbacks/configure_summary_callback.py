from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.services import db_service
from bot.utils.constants import LABELS, get_label, get_button_label
from bot.utils.logger import logger

logger = logger.get_logger(__name__)


async def configure_summary_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callback queries from the configuration menu."""
    try:
        query = update.callback_query
        
        # Check if callback is too old
        if not query:
            logger.warning("No callback query found in update")
            return
            
        try:
            await query.answer()
        except Exception as e:
            if "Query is too old" in str(e) or "query id is invalid" in str(e):
                logger.warning(f"Callback query too old or invalid: {e}")
                return
            else:
                raise
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        # Parse callback data
        parts = query.data.split("|")
        if len(parts) < 3 or parts[0] != "cfg":
            await query.answer("❌ Opción inválida")
            return

        field = parts[1]  # tone, length, language, include_names, daily_summary_hour
        action = parts[2]  # open, back_main, or a specific value

        # --- FIX START ---
        # Check permissions in group chats
        is_bot_admin = await db_service.is_user_admin(user_id)
        if not is_bot_admin and update.effective_chat.type in ["group", "supergroup"]:
            try:
                member = await context.bot.get_chat_member(chat_id, user_id)
                if member.status not in ["creator", "administrator"]:
                    await query.answer(
                        "❌ Solo los administradores pueden cambiar la configuración",
                        show_alert=True,
                    )
                    return
            except Exception as e:
                logger.warning(f"Failed to check user permissions: {e}")
                await query.answer("❌ Error al verificar permisos", show_alert=True)
                return
        # --- FIX END ---

        # Get current config and language
        config = await db_service.get_chat_summary_config(chat_id)
        language = config.get("language", "es")

        # Handle "open" action - show submenu
        if action == "open":
            await show_submenu(query, field, language, config, context)
            return

        # Handle "back to main menu" action
        if action == "back_main":
            await show_main_menu(query, context)
            return

        # Handle value selection
        try:
            # Update the database with new value
            if field == "include_names":
                # Convert string 'true'/'false' to boolean
                value = action.lower() == "true"
            else:
                value = action

            success = await db_service.update_chat_summary_config(
                chat_id, {field: value}
            )

            if success:
                # Show confirmation message
                if field == "daily_summary_hour":
                    if value == "off":
                        confirm_text = get_label("confirm_daily_off", language)
                    else:
                        confirm_text = (
                            f"{get_label('confirm_daily_hour', language)} {value}"
                        )
                else:
                    confirm_text = f"{get_label(f'confirm_{field}', language)} {get_button_label(field, str(value).lower(), language)}"

                try:
                    await query.answer(confirm_text)
                except Exception as e:
                    if "Query is too old" in str(e) or "query id is invalid" in str(e):
                        logger.warning(f"Cannot answer callback query - too old: {e}")
                    else:
                        raise
                        
                # If daily_summary_hour changed, update scheduler
                if field == "daily_summary_hour":
                    logger.debug(
                        f"Daily summary hour changed to {value} for chat {chat_id}"
                    )
                    try:
                        from bot.services.scheduler_service import scheduler_service

                        # Check if scheduler is running before attempting update
                        if not scheduler_service.scheduler.running:
                            logger.error(
                                f"Scheduler is not running, cannot update job for chat {chat_id}"
                            )
                            await query.answer(
                                "⚠️ Configuración guardada, pero el programador no está activo. Contacta al administrador.",
                                show_alert=True,
                            )
                            return

                        scheduler_service.update_daily_summary_job(chat_id, value)
                        logger.info(
                            f"✅ Successfully updated daily summary schedule for chat {chat_id} to {value}"
                        )  # Verify the job was created/updated and add next run time to confirmation
                        confirm_text_details = ""
                        if value != "off":
                            job_id = f"daily_summary_{chat_id}"
                            job = scheduler_service.scheduler.get_job(job_id)
                            if job:
                                import pytz
                                from datetime import datetime

                                next_run_utc = job.next_run_time
                                madrid_tz = pytz.timezone("Europe/Madrid")
                                next_run_madrid = next_run_utc.astimezone(madrid_tz)

                                # Loguear con más detalle
                                logger.info(
                                    f"Scheduler job for chat {chat_id} VERIFIED. Next run: {next_run_madrid.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                                )

                                # Añadir a la confirmación del usuario
                                confirm_text_details = f"\n*Próximo resumen programado para:* {next_run_madrid.strftime('%d de %b a las %H:%M')}"
                            else:
                                logger.error(
                                    f"Scheduler job verification FAILED for chat {chat_id}"
                                )
                                await query.answer(
                                    "⚠️ Configuración guardada, pero hubo un problema al verificar el trabajo en el programador.",
                                    show_alert=True,
                                )
                                return

                        # Update the confirmation message with next run details
                        if value == "off":
                            final_confirm_text = confirm_text
                        else:
                            final_confirm_text = confirm_text + confirm_text_details

                        try:
                            await query.answer(final_confirm_text)
                        except Exception as e:
                            if "Query is too old" in str(e) or "query id is invalid" in str(e):
                                logger.warning(f"Cannot answer final confirmation - too old: {e}")
                            else:
                                raise

                    except Exception as e:
                        logger.error(
                            f"❌ Failed to update scheduler for chat {chat_id}: {e}",
                            exc_info=True,
                        )
                        await query.answer(
                            "⚠️ Configuración guardada, pero hubo un problema con el programador. Contacta al administrador.",
                            show_alert=True,
                        )
                        return

                # Return to main menu
                await show_main_menu(query, context)
            else:
                await query.answer(get_label("error_db", language), show_alert=True)

        except Exception as e:
            logger.error(
                f"Error updating config for chat {chat_id}: {e}", exc_info=True
            )
            await query.answer(get_label("error_db", language), show_alert=True)

    except Exception as e:
        logger.error(f"Error in configure_summary_callback: {e}", exc_info=True)
        await update.callback_query.answer("❌ Error interno del bot", show_alert=True)


async def show_submenu(query, field, language, config, context):
    """Display a submenu for a specific configuration field."""
    try:
        chat_id = query.message.chat_id
        message_id = query.message.message_id

        # Create submenu title
        title = get_label(f"{field}_submenu_title", language)

        # Create buttons based on field type
        keyboard = []

        if field == "daily_summary_hour":
            # Generate dynamic buttons for all 24 hours

            # Button to disable
            is_off_current = config[field] == "off"
            off_button_text = (
                f"✅ {get_button_label(field, 'off', language)}"
                if is_off_current
                else get_button_label(field, "off", language)
            )
            keyboard.append(
                [
                    InlineKeyboardButton(
                        off_button_text, callback_data="cfg|daily_summary_hour|off"
                    )
                ]
            )

            # Generate buttons for each hour in a 4x6 grid
            row = []
            for hour in range(24):
                hour_str = f"{hour:02d}"  # Format "00", "01", etc.
                is_current = config[field] == hour_str
                button_text = f"✅ {hour_str}:00" if is_current else f"{hour_str}:00"

                row.append(
                    InlineKeyboardButton(
                        button_text, callback_data=f"cfg|daily_summary_hour|{hour_str}"
                    )
                )

                if len(row) == 4:  # 4 buttons per row
                    keyboard.append(row)
                    row = []
            if row:  # Add the last row if not complete
                keyboard.append(row)
        else:
            # Original logic for other fields (tone, length, etc.)
            if field in LABELS[language]["buttons"]:
                options = LABELS[language]["buttons"][field]
                row = []
                max_per_row = 3  # Keep original logic for other menus
                for key, label in options.items():
                    if field == "include_names":
                        is_current = str(config[field]).lower() == key.lower()
                    else:
                        is_current = config[field] == key
                    button_text = f"✅ {label}" if is_current else label
                    row.append(
                        InlineKeyboardButton(
                            button_text, callback_data=f"cfg|{field}|{key}"
                        )
                    )
                    if len(row) == max_per_row:
                        keyboard.append(row)
                        row = []
                if row:
                    keyboard.append(row)

        # Add back button
        keyboard.append(
            [
                InlineKeyboardButton(
                    get_label("back_button", language),
                    callback_data="cfg|field|back_main",
                )
            ]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Edit message to show submenu
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=title,
            reply_markup=reply_markup,
        )
        await query.answer()

    except Exception as e:
        logger.error(f"Error showing submenu for field {field}: {e}", exc_info=True)
        await query.answer("❌ Error al mostrar el submenú", show_alert=True)


async def show_main_menu(query, context):
    """Return to the main configuration menu."""
    try:
        chat_id = query.message.chat_id
        message_id = query.message.message_id

        # Get current config from database
        config = await db_service.get_chat_summary_config(chat_id)
        language = config.get("language", "es")

        # Create main menu message
        message_text = get_label("title_main", language) + "\n\n"

        # Add current settings
        message_text += f"🧠 {get_label('tone_label', language)}: {get_button_label('tone', config['tone'], language)}\n"
        message_text += f"📏 {get_label('length_label', language)}: {get_button_label('length', config['length'], language)}\n"
        message_text += f"🌐 {get_label('language_label', language)}: {get_button_label('language', config['language'], language)}\n"
        message_text += f"👥 {get_label('names_label', language)}: {get_button_label('include_names', 'true' if config['include_names'] else 'false', language)}\n"
        message_text += f"⏰ {get_label('hour_label', language)}: {get_button_label('daily_summary_hour', config['daily_summary_hour'], language)}\n"

        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    get_label("tone_button", language), callback_data="cfg|tone|open"
                ),
                InlineKeyboardButton(
                    get_label("length_button", language),
                    callback_data="cfg|length|open",
                ),
                InlineKeyboardButton(
                    get_label("language_button", language),
                    callback_data="cfg|language|open",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_label("names_button", language),
                    callback_data="cfg|include_names|open",
                ),
                InlineKeyboardButton(
                    get_label("hour_button", language),
                    callback_data="cfg|daily_summary_hour|open",
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Edit message to show main menu
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message_text,
            reply_markup=reply_markup,
        )
        await query.answer()

    except Exception as e:
        logger.error(f"Error returning to main menu: {e}", exc_info=True)
        await query.answer("❌ Error al volver al menú principal", show_alert=True)
