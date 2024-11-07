import asyncio
from dotenv import load_dotenv
from bot.utils.logger import logger
from bot.bot import telegram_bot
from bot.services.database_service import db_service
from bot.config import config  # Importamos la instancia

logger = logger.get_logger(__name__)

async def main():
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

        # Initialize database
        await db_service.initialize(config.DB_PATH)

        # Initialize and start the bot
        telegram_bot.initialize(
            config.BOT_TOKEN, config.OPENAI_API_KEY
        )

        await telegram_bot.start()
    except Exception as e:
        logger.error(f"Application failed to start: {e}", exc_info=True)
        raise
    finally:
        try:
            await telegram_bot.stop()
        except Exception as e:
            logger.error(f"Error stopping telegram bot: {e}")

        if not db_service.closed:
            try:
                await db_service.close()
            except Exception as e:
                logger.error(f"Error closing database: {e}")


if __name__ == "__main__":
    asyncio.run(main())
