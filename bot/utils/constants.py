import re

# Regular expression to match YouTube video IDs
YOUTUBE_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(?:embed\/)?(?:v\/)?(?:shorts\/)?(?:live\/)?(?:[\w\-]{11})"
)

# Regular expression to match article URLs
ARTICLE_URL_REGEX = re.compile(r"https?:\/\/\S+")

# Maximum size for a single message chunk (in characters)
CHUNK_SIZE = 4096

# Delay between sending chunks of messages (in seconds)
PAUSE_BETWEEN_CHUNKS = 0.5

# Maximum file size for audio/video processing (20 MB in bytes)
MAX_FILE_SIZE = 20 * 1024 * 1024

# Supported MIME types
SUPPORTED_AUDIO_TYPES = [
    'audio/mpeg', 'audio/mp4', 'audio/ogg',
    'audio/wav', 'audio/webm', 'audio/x-wav'
]

SUPPORTED_VIDEO_TYPES = [
    'video/mp4', 'video/mpeg', 'video/ogg',
    'video/webm', 'video/quicktime'
]

SUPPORTED_DOCUMENT_TYPES = [
    'text/plain', 'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

# Database cleanup thresholds
CLEANUP_THRESHOLDS = {
    'DAYS_TO_KEEP': 30,              # Keep messages for 30 days
    'MINIMUM_MESSAGES': 1000,        # Always keep at least 1000 messages per chat
    'CLEANUP_THRESHOLD': 10000,      # Trigger cleanup when chat reaches 10000 messages
    'CLEANUP_INTERVAL': 24 * 60 * 60, # Cleanup interval in seconds (24 hours)
    'MAX_SUMMARY_LENGTH': 2000       # Maximum length for summaries
}

# Message limits
MAX_FILE_SIZE = 20 * 1024 * 1024    # 20MB in bytes
PAUSE_BETWEEN_CHUNKS = 0.5          # Seconds between message chunks
