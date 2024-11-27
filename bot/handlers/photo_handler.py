import base64
import aiohttp
from telegram import Message
from telegram.ext import CallbackContext
from bot.services import openai_service
from bot.utils.logger import logger

logger = logger.get_logger(__name__)


async def photo_handler(message: Message, context: CallbackContext) -> str:
    """
    Handle photo analysis requests.
    Args:
        message: Telegram message containing photo
        context: Callback context
    Returns:
        str: Raw content for the photo analysis
    """
    try:
        # Get highest resolution photo
        photo = message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        logger.info(
            f"Processing photo from user {message.from_user.id}, file_id: {photo.file_id}"
        )

        try:
            # Download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(file.file_path) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download image: {response.status}")
                        await message.reply_text(
                            "No pude descargar la imagen. Por favor, inténtalo de nuevo."
                        )
                        return None
                    image_data = await response.read()

            # Convert to base64
            base64_image = base64.b64encode(image_data).decode("utf-8")
            logger.info("Image successfully processed and converted to base64")
            return f"data:image/jpeg;base64,{base64_image}"

        except Exception as e:
            logger.error(f"Error downloading/processing image: {str(e)}", exc_info=True)
            await message.reply_text(
                "Hubo un problema al procesar la imagen. Por favor, inténtalo de nuevo."
            )
            return None

    except Exception as e:
        logger.error(f"Error in photo_handler: {str(e)}", exc_info=True)
        await message.reply_text(
            "Ocurrió un error inesperado al procesar la imagen. Por favor, inténtalo de nuevo."
        )
        return None
