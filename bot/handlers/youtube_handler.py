import re
from telegram import Update
from telegram.ext import CallbackContext
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    VideoUnavailable,
)
from typing import Optional

from bot.utils.constants import YOUTUBE_REGEX
from bot.utils.logger import logger

logger = logger.get_logger(__name__)

async def youtube_handler(
    update: Update, context: CallbackContext, youtube_url: str
) -> Optional[str]:
    """
    Handle YouTube video transcription requests.

    Args:
        update: Telegram update object
        context: Callback context
        youtube_url: URL of the YouTube video

    Returns:
        Optional[str]: Transcription text if successful, None otherwise
    """
    user_id = update.effective_user.id

    logger.debug(f"=== YOUTUBE HANDLER STARTED ===")
    logger.debug(f"User ID: {user_id}")
    logger.debug(f"YouTube URL: {youtube_url}")

    # Extract video ID
    video_id = extract_video_id(youtube_url)
    if not video_id:
        logger.error(f"Could not extract video ID from URL: {youtube_url}")
        await update.message.chat.send_message(
            "No se pudo extraer el ID del video de YouTube."
        )
        return None

    logger.info(f"Processing YouTube video {video_id} for user {user_id}")

    try:
        # Get available transcripts
        logger.debug(f"Requesting transcript list for video {video_id}")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = [t.language_code for t in transcript_list]
        logger.info(f"Available transcripts for video {video_id}: {available_languages}")

        # Try to get English transcript first, fall back to first available
        transcript = next(
            (t for t in transcript_list if t.language_code == "en"),
            next(iter(transcript_list)),
        )
        selected_language = transcript.language_code
        logger.info(f"Selected transcript language: {selected_language}")

        # Fetch and process transcript
        logger.debug(f"Fetching transcript data for language: {selected_language}")
        transcript_data = transcript.fetch()
        transcript_entries = len(transcript_data)
        logger.debug(f"Retrieved {transcript_entries} transcript entries")

        transcription = " ".join([entry.text for entry in transcript_data])
        transcription_length = len(transcription)

        logger.info(f"Transcription fetched successfully, length: {transcription_length} chars")
        logger.debug(f"Transcription preview: {transcription[:200]}...")

        return transcription

    except NoTranscriptFound:
        logger.warning(f"No transcripts available for video {video_id}")
        await update.message.chat.send_message(
            "El video no tiene subtítulos disponibles."
        )
    except VideoUnavailable:
        logger.error(f"Video {video_id} is unavailable")
        await update.message.chat.send_message(
            "No se pudo procesar debido a problemas con el enlace proporcionado."
        )
    except Exception as e:
        logger.error(f"Unexpected error processing YouTube video {video_id}: {str(e)}", exc_info=True)
        await update.message.chat.send_message(
            "Ocurrió un error inesperado al procesar la transcripción."
        )

    logger.debug(f"=== YOUTUBE HANDLER FAILED ===")
    return None


def extract_video_id(youtube_url):
    # Extract the video ID from a YouTube URL using regex.
    video_id_match = YOUTUBE_REGEX.search(youtube_url)
    if video_id_match:
        return re.search(r"([\w\-]{11})", youtube_url).group(1)
    return None