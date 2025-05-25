import re
from typing import List

# Regular expressions
YOUTUBE_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(?:embed\/)?(?:v\/)?(?:shorts\/)?(?:live\/)?(?:[\w\-]{11})"
)
ARTICLE_URL_REGEX = re.compile(r"https?:\/\/\S+")

# Message handling
CHUNK_SIZE = 4096  # Maximum characters per message
PAUSE_BETWEEN_CHUNKS = 0.5  # Seconds between message chunks
MAX_RECENT_MESSAGES = 300  # Maximum messages to fetch for summarization

# File handling
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

# Supported MIME types
SUPPORTED_AUDIO_TYPES: List[str] = [
    "audio/mpeg",
    "audio/mp4",
    "audio/ogg",
    "audio/wav",
    "audio/webm",
    "audio/x-wav",
]

SUPPORTED_VIDEO_TYPES: List[str] = [
    "video/mp4",
    "video/mpeg",
    "video/ogg",
    "video/webm",
    "video/quicktime",
]

SUPPORTED_DOCUMENT_TYPES: List[str] = [
    "text/plain",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]

# Cooldowns and Limits for /summarize
COOLDOWN_TEXT_SIMPLE_SECONDS = 120  # 2 minutes
COOLDOWN_ADVANCED_SECONDS = 600    # 10 minutes
DAILY_LIMIT_ADVANCED_OPS = 5

# Operation Types
OPERATION_TYPE_TEXT_SIMPLE = "text_simple"
OPERATION_TYPE_ADVANCED = "advanced"

# Message Strings for Limits
MSG_DAILY_LIMIT_REACHED = "Has alcanzado el límite diario de {limit} operaciones avanzadas. Inténtalo de nuevo mañana, figura."
MSG_COOLDOWN_ACTIVE = "Machooo, espérate un poco antes de volver a usar el comando ({remaining}s)."
