import logging
from telegram.ext import CallbackContext
from telegram import Update
from bot.utils.decorators import premium_only, log_command
from bot.utils.logger import logger

logger = logger.get_logger(__name__)

# TODO implement
@premium_only()
@log_command()
async def summarize_command(update: Update, context: CallbackContext) -> None:
    # TODO implement
    pass
