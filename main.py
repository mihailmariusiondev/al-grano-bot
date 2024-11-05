import asyncio
from dotenv import load_dotenv
from bot.utils.logger import logger
from bot.bot import telegram_bot
from bot.services.database_service import db_service
from bot.config import config  # Importamos la instancia


async def main():
    main_logger = logger.get_logger("al-grano-bot.main")
    try:
        # Load environment variables
        load_dotenv()
        # Load configuration
        config.load_from_env()

        if not config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is not set")
        if not config.OPENAI_API_KEY:
            main_logger.warning("OPENAI_API_KEY not set. AI features will be disabled.")

        main_logger.info("Starting Telegram Bot application...")
        # Initialize database
        await db_service.initialize(config.DB_PATH)  # Usamos la config
        # Initialize and start the bot
        telegram_bot.initialize(
            config.BOT_TOKEN, config.OPENAI_API_KEY
        )  # Usamos la config
        await telegram_bot.start()
    except Exception as e:
        main_logger.error(f"Application failed to start: {e}", exc_info=True)
        raise
    finally:
        try:
            await telegram_bot.stop()  # Esto ya cierra la DB
        except Exception as e:
            main_logger.error(f"Error stopping telegram bot: {e}")

        if not db_service.closed:  # Ahora podemos usar la propiedad
            try:
                await db_service.close()
            except Exception as e:
                main_logger.error(f"Error closing database: {e}")


if __name__ == "__main__":
    asyncio.run(main())
