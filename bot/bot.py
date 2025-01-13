from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from typing import Optional
from bot.commands import (
    start_command,
    help_command,
    summarize_command,
    toggle_daily_summary_command,
)
from bot.handlers import (
    error_handler,
    message_handler,
)
from bot.services.openai_service import openai_service
from bot.utils.logger import logger
from bot.services.database_service import db_service
from bot.services.scheduler_service import scheduler_service
from bot.services.message_service import message_service
import asyncio


class TelegramBot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self, token: str, openai_api_key: Optional[str] = None):
        """Initialize the Telegram bot"""
        if not self.initialized:
            self.token = token
            self.logger = logger.get_logger(__name__)

            if openai_api_key:
                openai_service.initialize(openai_api_key)

            self.application: Optional[Application] = None
            self.initialized = True

    def register_handlers(self):
        if not self.initialized:
            raise RuntimeError("Telegram bot not initialized")

        self.logger.info("Registering handlers...")

        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("summarize", summarize_command))
        self.application.add_handler(
            CommandHandler("toggle_daily_summary", toggle_daily_summary_command)
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
        )

        self.application.add_error_handler(error_handler)

        self.logger.info("All handlers registered successfully")

    async def _start_scheduler(self):
        """Start scheduler in the running event loop"""
        try:
            scheduler_service.start()
            self.logger.info("Scheduler started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}", exc_info=True)
            raise

    def start(self):
        if not self.initialized:
            raise RuntimeError("Telegram bot not initialized")
        try:
            self.logger.info("Starting bot initialization...")
            self.application = (
                ApplicationBuilder()
                .token(self.token)
                .read_timeout(30)
                .write_timeout(30)
                .connect_timeout(30)
                .build()
            )
            self.register_handlers()

            # Initialize message service with bot instance
            message_service.initialize(self.application.bot)

            # Create and set event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Start scheduler in the event loop
            loop.run_until_complete(self._start_scheduler())

            self.logger.info("Starting bot polling...")
            self.application.run_polling()

        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}", exc_info=True)
            raise

    async def stop(self):
        if self.application:
            self.logger.info("Stopping bot...")
            # Stop the scheduler
            scheduler_service.stop()
            await self.application.stop()
            await db_service.close()
            self.logger.info("Bot stopped successfully")


telegram_bot = TelegramBot()
