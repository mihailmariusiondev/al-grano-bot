import asyncio
from dotenv import load_dotenv
from bot.utils.logger import logger
from bot.bot import telegram_bot
from bot.services.database_service import db_service
from bot.config import config

logger = logger.get_logger(__name__)


def main():
    try:
        # Load environment variables
        load_dotenv()

        # Load configuration
        config.load_from_env()

        if not config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is not set")
        if not config.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. AI features will be disabled.")

        logger.info("Starting Telegram Bot application...")
        logger.info(f"Initializing database with path: {config.DB_PATH}")

        # Initialize database asynchronously
        asyncio.run(db_service.initialize(config.DB_PATH))

        # Add the following lines to set a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Initialize and start the bot
        telegram_bot.initialize(config.BOT_TOKEN, config.OPENAI_API_KEY)
        telegram_bot.start()

    except Exception as e:
        logger.error(f"Application failed to start: {e}", exc_info=True)
        raise

    finally:
        # Stop the bot if needed
        try:
            # Await the stop coroutine properly
            asyncio.run(telegram_bot.stop())
        except Exception as e:
            logger.error(f"Error stopping telegram bot: {e}")

        # Close database connection asynchronously
        if not db_service.closed:
            try:
                asyncio.run(db_service.close())
            except Exception as e:
                logger.error(f"Error closing database: {e}")


if __name__ == "__main__":
    main()
