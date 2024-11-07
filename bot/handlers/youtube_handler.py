import re
from telegram import Update
from telegram.ext import CallbackContext
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    VideoUnavailable,
)
import logging

from bot.utils.constants import YOUTUBE_REGEX

logging = logging.getLogger(__name__)

async def youtube_handler(
    update: Update, context: CallbackContext, youtube_url: str
) -> None:
    """
    Handle YouTube video transcription requests.

    Args:
        update: Telegram update object
        context: Callback context
        youtube_url: URL of the YouTube video
    """
    user_id = update.effective_user.id

    # Extract video ID
    video_id = extract_video_id(youtube_url)

    logging.info(f"Processing YouTube video {video_id} for user {user_id}")

    try:
        # Get available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        logging.info(
            f"Available transcripts for video {video_id}: {[t.language_code for t in transcript_list]}"
        )

        # Try to get English transcript first, fall back to first available
        transcript = next(
            (t for t in transcript_list if t.language_code == "en"),
            next(iter(transcript_list)),
        )
        logging.info(f"Selected transcript language: {transcript.language_code}")

        # Fetch and process transcript
        transcript_data = transcript.fetch()
        transcription = " ".join([entry["text"] for entry in transcript_data])
        logging.info(f"Transcription fetched, length: {len(transcription)} chars")

        return transcription

    except NoTranscriptFound:
        logging.warning(f"No transcripts available for video {video_id}")
        await update.message.chat.send_message(
            "El video no tiene subtítulos disponibles."
        )
    except VideoUnavailable:
        logging.error(f"Video {video_id} is unavailable")
        await update.message.chat.send_message(
            "No se pudo procesar debido a problemas con el enlace proporcionado."
        )
    except Exception as e:
        logging.error(f"Error processing YouTube video {video_id}: {str(e)}")
        await update.message.chat.send_message(
            "Ocurrió un error inesperado al procesar la transcripción."
        )


def extract_video_id(youtube_url):
    # Extract the video ID from a YouTube URL using regex.
    video_id_match = YOUTUBE_REGEX.search(youtube_url)
    if video_id_match:
        return re.search(r"([\w\-]{11})", youtube_url).group(1)
    return None