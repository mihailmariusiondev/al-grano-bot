from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from ..config import config
import time
from ..utils.logger import logger
from ..services import db_service
import asyncio
import random

logger = logger.get_logger("utils.decorators")

COOLDOWN_REPLIES = [
    "Machooo, espérate un poco antes de volver a usar el comando",
    "Tranquilo, fiera, dale un respiro al comando. Deja que se enfríe un poco.",
    "Eh, campeón, no te embales. Espera un momento antes de darle al comando otra vez.",
    "Frena el carro, máquina. Deja que el comando descanse un poquito antes de volver a usarlo.",
    "Para el carro, figura. El comando necesita un descanso antes de que lo vuelvas a machacar.",
    "Quieto ahí, crack. Deja que el comando se tome un respiro antes de darle de nuevo.",
    "Eh, machote, no te aceleres. El comando necesita un descanso antes de volver a la acción.",
    "Calma tus ansias, tío. Deja que el comando se recupere antes de volver a darle caña.",
    "Tranqui, tronco. El comando necesita un momento para recargar pilas. Espera un poco.",
    "Relájate, cabronazo. No atosigues al comando. Dale un respiro antes de usarlo de nuevo.",
    "Eeeh, campeón, baja el ritmo. El comando necesita un descanso antes de volver al ruedo.",
    "No te embales, mastodonte. Deja que el comando se tome un momento antes de volver a la carga.",
    "Tranquilo, figurita. El comando necesita recuperarse antes de que lo vuelvas a machacar.",
    "Para el carro, machote. No sobrecarges el comando. Espera un poco antes de usarlo otra vez.",
    "Eh, crack, dale un respiro al comando. No lo presiones tanto, necesita un descanso.",
    "Frena un poco, tipazo. El comando necesita un momento para coger aire antes de seguir.",
    "Calma, fiera. No acribilles al comando. Deja que se recupere antes de volver a darle.",
    "Tranquilo, machoman. El comando necesita un pequeño descanso antes de volver a la acción.",
    "Para el carro, mastodonte. Deja que el comando se tome un respiro antes de seguir.",
    "Eh, figura, no te precipites. El comando necesita un momento para recargar antes de continuar.",
    "Tranqui, campeón. No sobrecarges el comando. Dale un poco de tiempo para recuperarse.",
    "Eeeh, crack, no te embales. Deja que el comando se tome un descanso antes de volver.",
    "Calma tus ansias, machote. El comando necesita un respiro antes de seguir a tope.",
    "Para el carro, fiera. No presiones tanto al comando. Necesita un momento para reponerse.",
    "Tranquilo, tronco. Deja que el comando coja aire antes de volver a darle caña.",
    "Eh, figura, no te aceleres. El comando necesita un pequeño descanso antes de seguir.",
    "Frena un poco, campeón. No atosigues al comando. Dale un respiro antes de continuar.",
    "Calma, machoman. Deja que el comando se recupere antes de volver a la carga.",
    "Tranqui, mastodonte. El comando necesita un momento para recargar pilas antes de seguir.",
    "Para el carro, crack. No presiones tanto al comando. Necesita un descanso antes de volver.",
]


def admin_command(func):
    """
    Decorator to restrict command access to admin users only
    """

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


def rate_limit_by_chat(seconds: int):
    """Rate limit by chat instead of user"""
    cooldowns = {}
    lock = asyncio.Lock()

    def decorator(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id
            async with lock:
                current_time = time.time()
                last_time = cooldowns.get(chat_id, 0)
                if current_time - last_time < seconds:
                    remaining = int(seconds - (current_time - last_time))
                    cooldown_message = random.choice(COOLDOWN_REPLIES)
                    await update.message.reply_text(
                        f"{cooldown_message} ({remaining}s)"
                    )
                    return
                cooldowns[chat_id] = current_time
            return await func(update, context)

        return wrapped

    return decorator


def premium_only():
    """
    Decorator to restrict command access to premium users only
    """

    def decorator(func):
        @wraps(func)
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

    return decorator


def log_command():
    """
    Decorator to log command usage with extended user information
    """

    def decorator(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            command = update.message.text

            # Build user info string with available fields
            user_info = [
                f"ID: {user.id}",
                f"Username: @{user.username}" if user.username else None,
                f"Name: {user.first_name}" if user.first_name else None,
                f"Last Name: {user.last_name}" if user.last_name else None,
            ]

            # Filter out None values and join
            user_details = " | ".join([info for info in user_info if info])

            logger.info(f"Command executed by [{user_details}]: {command}")

            return await func(update, context)

        return wrapped

    return decorator


def bot_started():
    """
    Decorator to check if bot is started in the chat
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context, *args, **kwargs):
            if not update.effective_chat:
                return
            chat_id = update.effective_chat.id
            chat_state = await db_service.get_chat_state(chat_id)
            if not chat_state or not chat_state.get("is_bot_started"):
                logger.warning(f"Bot not started for chat_id: {chat_id}")
                await update.message.reply_text(
                    "Por favor, inicia el bot primero usando el comando /start"
                )
                return
            return await func(update, context, *args, **kwargs)

        return wrapper

    return decorator
