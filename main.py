import asyncio
from dotenv import load_dotenv
from bot.utils.logger import logger
from bot.bot import telegram_bot
from bot.services.database_service import db_service
from bot.config import config
from typing import Set

logger = logger.get_logger(__name__)


async def init_database():
    """Initialize database asynchronously"""
    await db_service.initialize(config.DB_PATH)


async def setup_auto_admins(admin_ids: Set[int]):
    """Ensure specified user IDs are set as admins."""
    if not admin_ids:
        logger.info("No auto-admin user IDs configured.")
        return

    logger.info(f"Setting up auto-admin users for IDs: {admin_ids}")
    for user_id in admin_ids:
        try:
            # Ensure user exists in the database
            await db_service.get_or_create_user(
                user_id=user_id,
                username=f"AutoAdmin{user_id}",  # Placeholder
                first_name="Bot",  # Placeholder
                last_name="Admin"  # Placeholder
            )

            # Set is_admin flag
            await db_service.update_user_fields(user_id, {"is_admin": True})
            logger.info(f"User {user_id} ensured and set as admin.")
        except Exception as e:
            logger.error(f"Failed to set user {user_id} as auto-admin: {e}", exc_info=True)


def main():
    # Set up the event loop for the main thread
    # This loop will be used by PTB's run_polling
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        load_dotenv(override=True)
        config.load_from_env()

        if not config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is not set")
        if not config.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. AI features will be disabled.")

        logger.info("Starting Telegram Bot application...")
        logger.info(f"Initializing database with path: {config.DB_PATH}")

        loop.run_until_complete(init_database())

        # Setup auto-admin users
        if config.AUTO_ADMIN_USER_IDS:
            logger.info(f"Configuring auto-admin users: {config.AUTO_ADMIN_USER_IDS}")
            loop.run_until_complete(setup_auto_admins(config.AUTO_ADMIN_USER_IDS))
        else:
            # Optional: Set default admin ID if no IDs are configured
            logger.info("No AUTO_ADMIN_USER_IDS from env. Setting default admin ID 6025856.")
            loop.run_until_complete(setup_auto_admins({6025856}))

        telegram_bot.initialize(config.BOT_TOKEN, config.OPENAI_API_KEY)
        # telegram_bot.start() will now block until CTRL+C or other shutdown.
        # It internally calls run_polling.
        # Scheduler start is handled within telegram_bot.start() on the correct loop.
        telegram_bot.start()

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt (CTRL+C) received. PTB will handle the shutdown sequence.")
        # PTB's run_polling catches SIGINT and initiates shutdown,
        # which includes calling any registered post_shutdown hooks.
        # No explicit calls to telegram_bot.stop() or db_service.close() are needed here
        # as they are handled by the _custom_cleanup hook.

    except Exception as e:
        logger.error(f"Application failed with an unhandled error: {e}", exc_info=True)
        # If a critical error happens before or during PTB's run_polling,
        # the post_shutdown hooks might not run. Consider if manual cleanup is needed here
        # for such specific failure scenarios, but for CTRL+C this should be fine.

    finally:
        logger.info("Main function's 'finally' block reached.")

        # The event loop is primarily managed and closed by PTB's Application.shutdown().
        # We should avoid interfering with its closure unless there's a specific reason.
        current_active_loop = asyncio.get_event_loop_policy().get_event_loop()
        if not current_active_loop.is_closed():
            logger.info("Event loop is not closed in main's finally. PTB should handle this.")
            # loop.close() # Avoid force-closing if PTB is expected to do it.
        else:
            logger.info("Event loop was already closed.")

        logger.info("Application shutdown process in main has finished.")


if __name__ == "__main__":
    main()
