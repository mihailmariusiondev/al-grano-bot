from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from typing import Optional
from bot.commands import (
    start_command,
    help_command,
    summarize_command,
    configure_summary_command,
    export_chat_command,
)
from bot.handlers import (
    error_handler,
    message_handler,
)
from bot.callbacks import configure_summary_callback
from bot.utils.logger import logger
from bot.services.database_service import db_service
from bot.services.scheduler_service import scheduler_service
from bot.services.message_service import message_service
from telegram import Update
from telegram.ext import ContextTypes
import asyncio

async def obsolete_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle obsolete commands by redirecting to the new configuration command."""
    await update.message.reply_text(
        "Este comando ya no existe. Usa /configurar_resumen para personalizar los resúmenes."
    )

class TelegramBot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self, token: str):
        """Initialize the Telegram bot"""
        if not self.initialized:
            self.token = token
            self.logger = logger.get_logger(__name__)
            self.application: Optional[Application] = None
            self.initialized = True

    async def _custom_cleanup(self, application: Optional[Application] = None):
        """Custom cleanup logic to be called by PTB's post_shutdown."""
        self.logger.info("Executing custom cleanup via PTB post_shutdown...")
        if scheduler_service.scheduler.running:
            self.logger.info("Stopping scheduler service...")
            scheduler_service.stop()
            self.logger.info("Scheduler service stop initiated.")
        else:
            self.logger.info("Scheduler service was not running or already stopped.")

        if db_service and not db_service.closed:
            self.logger.info("Closing database service connection...")
            try:
                await db_service.close()
                self.logger.info("Database service connection closed.")
            except Exception as e:
                self.logger.error(f"Error closing database service during cleanup: {e}", exc_info=True)
        else:
            self.logger.info("Database service was already closed or not initialized.")
        self.logger.info("Custom cleanup via PTB post_shutdown finished.")

    def register_handlers(self):
        if not self.initialized:
            raise RuntimeError("Telegram bot not initialized")

        self.logger.debug("=== REGISTERING BOT HANDLERS ===")

        # Command handlers
        self.logger.debug("Registering command handlers...")
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("summarize", summarize_command))
        self.application.add_handler(CommandHandler("configurar_resumen", configure_summary_command))
        self.application.add_handler(CommandHandler("export_chat", export_chat_command))
        self.logger.debug("Core command handlers registered")

        # Obsolete command handlers
        self.logger.debug("Registering obsolete command handlers...")
        self.application.add_handler(CommandHandler("toggle_daily_summary", obsolete_command_handler))
        self.application.add_handler(CommandHandler("toggle_summary_type", obsolete_command_handler))
        self.logger.debug("Obsolete command handlers registered")

        # Callback handlers
        self.logger.debug("Registering callback handlers...")
        self.application.add_handler(
            CallbackQueryHandler(configure_summary_callback, pattern=r'^cfg\|')
        )
        self.logger.debug("Callback handlers registered")

        # Message handlers
        self.logger.debug("Registering message handlers...")
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
        )
        self.logger.debug("Message handlers registered")

        # Error handler
        self.logger.debug("Registering error handler...")
        self.application.add_error_handler(error_handler)
        self.logger.debug("Error handler registered")

        self.logger.info("=== ALL HANDLERS REGISTERED SUCCESSFULLY ===")

    async def _start_scheduler(self):
        """Start scheduler in the running event loop"""
        try:
            await scheduler_service.start()
            self.logger.info("Scheduler started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}", exc_info=True)
            raise

    def start(self):
        if not self.initialized:
            raise RuntimeError("Telegram bot not initialized")

        self.logger.info("=== TELEGRAM BOT STARTUP STARTED ===")
        self.logger.debug(f"Bot token: {self.token[:10]}...")

        try:
            self.logger.info("Building Telegram Bot application...")
            self.application = (
                ApplicationBuilder()
                .token(self.token)
                .read_timeout(30)
                .write_timeout(30)
                .connect_timeout(30)
                .post_shutdown(self._custom_cleanup)
                .build()
            )
            self.logger.debug("Application builder configured with timeouts and cleanup")

            self.register_handlers()
            message_service.initialize(self.application.bot)
            self.logger.debug("Message service initialized")

            current_loop = asyncio.get_event_loop_policy().get_event_loop()
            self.logger.debug(f"Current event loop running: {current_loop.is_running()}")

            if current_loop.is_running():
                 asyncio.create_task(self._start_scheduler())
                 self.logger.debug("Scheduler started as async task")
            else:
                 current_loop.run_until_complete(self._start_scheduler())
                 self.logger.debug("Scheduler started in event loop")

            self.logger.info("=== STARTING BOT POLLING ===")
            self.application.run_polling()
            self.logger.info("=== BOT POLLING HAS STOPPED ===")
        except Exception as e:
            self.logger.error(f"=== BOT STARTUP FAILED ===")
            self.logger.error(f"Failed to start or run bot: {e}", exc_info=True)
            raise

    async def stop(self):
        if self.application:
            self.logger.info("TelegramBot.stop() called (programmatic stop)...")
            await self.application.stop()
            self.logger.info("TelegramBot.stop() finished (delegated to PTB shutdown).")
        else:
            self.logger.info("TelegramBot.stop() called, but application not initialized.")

telegram_bot = TelegramBot()
