import asyncio
from dotenv import load_dotenv
from bot.utils.logger import logger
from bot.bot import telegram_bot
from bot.services.database_service import db_service
from bot.config import config

logger = logger.get_logger(__name__)


async def init_database():
    """Initialize database asynchronously"""
    await db_service.initialize(config.DB_PATH)


def main():
    try:
        # Load environment variables, overriding existing ones
        load_dotenv(override=True)

        # Load configuration
        config.load_from_env()

        if not config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is not set")

        if not config.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. AI features will be disabled.")

        logger.info("Starting Telegram Bot application...")
        logger.info(f"Initializing database with path: {config.DB_PATH}")

        # Initialize database
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(init_database())

        # Initialize and start the bot
        telegram_bot.initialize(config.BOT_TOKEN, config.OPENAI_API_KEY)
        telegram_bot.start()

    except Exception as e:
        logger.error(f"Application failed to start: {e}", exc_info=True)
        raise
    finally:
        # Stop the bot if needed
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(telegram_bot.stop())
        except Exception as e:
            logger.error(f"Error stopping telegram bot: {e}")
        # Close database connection
        if not db_service.closed:
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(db_service.close())
            except Exception as e:
                logger.error(f"Error closing database: {e}")
        # Close the event loop
        try:
            loop.close()
        except Exception as e:
            logger.error(f"Error closing event loop: {e}")


if __name__ == "__main__":
    main()
