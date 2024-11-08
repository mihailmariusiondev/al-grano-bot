import logging
from typing import Optional
import requests
from readability import Document

logger = logging.getLogger(__name__)


async def article_handler(url: str) -> Optional[str]:
    """
    Handle web article summarization requests.
    Args:
        url: URL of the article to summarize
    Returns:
        str: Summary of the article or None if failed
    """
    logger.info(f"Processing article URL: {url}")

    try:
        # Fetch article content
        response = requests.get(url)
        doc = Document(response.content)

        # Get title and content
        article_title = doc.title()
        article_content = doc.summary()

        # Format content for summarization
        full_content = f"Title: {article_title}\n\nContent: {article_content}"

        return full_content

    except Exception as e:
        logger.error(f"Error processing article: {str(e)}", exc_info=True)
        return None
