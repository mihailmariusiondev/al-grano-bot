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
