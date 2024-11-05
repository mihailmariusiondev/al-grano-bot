from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from ..config import config
import time
from ..utils.logger import logger
from ..services import db_service
import asyncio

logger = logger.get_logger("utils.decorators")


def admin_command(func):
    @wraps(func)
    async def wrapped(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user_id = update.effective_user.id
        if not config.ADMIN_USERS or user_id not in config.ADMIN_USERS:
            await update.message.reply_text(
                "Este comando es solo para administradores."
            )
            return
        return await func(update, context, *args, **kwargs)

    return wrapped


def rate_limit(seconds: int):
    cooldowns = {}
    lock = asyncio.Lock()

    def decorator(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id

            async with lock:
                current_time = time.time()
                last_time = cooldowns.get(user_id, 0)

                if current_time - last_time < seconds:
                    remaining = int(seconds - (current_time - last_time))
                    await update.message.reply_text(
                        f"Por favor espera {remaining} segundos antes de usar este comando nuevamente."
                    )
                    return

                cooldowns[user_id] = current_time

            return await func(update, context)
        return wrapped
    return decorator


def premium_only(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        is_premium = await db_service.is_premium_user(user_id)

        if not is_premium:
            await update.message.reply_text(
                "Este comando es solo para usuarios premium!"
            )
            return

        return await func(update, context)

    return wrapped


def log_command(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        command = update.message.text
        logger.info(f"Usuario {user_id} ejecutó el comando: {command}")

        return await func(update, context)

    return wrapped
