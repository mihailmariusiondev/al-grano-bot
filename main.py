import asyncio
from dotenv import load_dotenv
from bot.utils.logger import logger
from bot.bot import telegram_bot
from bot.services.database_service import db_service
from bot.services.openai_service import openai_service # Asegurarse de importar openai_service
from bot.config import config
from typing import Set

logger = logger.get_logger(__name__)

async def init_database():
    """Initialize database asynchronously"""
    await db_service.initialize(config.DB_PATH)

async def init_ai_services():
    """Initialize AI related services"""
    if config.OPENROUTER_API_KEY and config.OPENAI_API_KEY:
        logger.info("Initializing OpenAIService with OpenRouter and OpenAI API keys...")
        openai_service.initialize(
            openrouter_api_key=config.OPENROUTER_API_KEY,
            openai_api_key=config.OPENAI_API_KEY, # Para Whisper
            openrouter_site_url=config.OPENROUTER_SITE_URL,
            openrouter_site_name=config.OPENROUTER_SITE_NAME
        )
        logger.info("OpenAIService initialized.")
    else:
        logger.warning("OpenRouter API key or OpenAI API key (for Whisper) not set. AI features requiring them might be disabled or fail.")

async def setup_auto_admins(admin_ids: Set[int]):
    """Ensure specified user IDs are set as admins."""
    if not admin_ids:
        logger.info("No auto-admin user IDs configured.")
        return
    logger.info(f"Setting up auto-admin users for IDs: {admin_ids}")
    for user_id in admin_ids:
        try:
            await db_service.get_or_create_user(
                user_id=user_id,
                username=f"AutoAdmin{user_id}",
                first_name="Bot",
                last_name="Admin"
            )
            await db_service.update_user_fields(user_id, {"is_admin": True})
            logger.info(f"User {user_id} ensured and set as admin.")
        except Exception as e:
            logger.error(f"Failed to set user {user_id} as auto-admin: {e}", exc_info=True)

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        load_dotenv(override=True)
        config.load_from_env() # Carga toda la configuración, incluidas las nuevas claves y URLs

        if not config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is not set")

        logger.info("Starting Telegram Bot application...")
        logger.info(f"Initializing database with path: {config.DB_PATH}")
        loop.run_until_complete(init_database())

        # Inicializar servicios de IA
        loop.run_until_complete(init_ai_services()) # Nueva llamada

        if config.AUTO_ADMIN_USER_IDS:
            logger.info(f"Configuring auto-admin users: {config.AUTO_ADMIN_USER_IDS}")
            loop.run_until_complete(setup_auto_admins(config.AUTO_ADMIN_USER_IDS))
        else:
            logger.info("No AUTO_ADMIN_USER_IDS from env. Setting default admin ID 6025856.")
            loop.run_until_complete(setup_auto_admins({6025856}))

        # TelegramBot.initialize ahora solo necesita el token
        telegram_bot.initialize(token=config.BOT_TOKEN)

        telegram_bot.start()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt (CTRL+C) received. PTB will handle the shutdown sequence.")
    except Exception as e:
        logger.error(f"Application failed with an unhandled error: {e}", exc_info=True)
    finally:
        logger.info("Main function's 'finally' block reached.")
        current_active_loop = asyncio.get_event_loop_policy().get_event_loop()
        if not current_active_loop.is_closed():
            logger.info("Event loop is not closed in main's finally. PTB should handle this.")
        else:
            logger.info("Event loop was already closed.")
        logger.info("Application shutdown process in main has finished.")

if __name__ == "__main__":
    main()
