from typing import Optional
import requests
from readability import parse
from bot.utils.logger import logger

logger = logger.get_logger(__name__)


async def article_handler(url: str) -> Optional[str]:
    """
    Handle web article summarization requests.
    Args:
        url: URL of the article to summarize
    Returns:
        str: Summary of the article or None if failed
    """
    logger.debug(f"=== ARTICLE HANDLER STARTED ===")
    logger.debug(f"URL: {url}")
    logger.info(f"Processing article URL: {url}")

    try:
        # Fetch article content
        logger.debug("Fetching article content via HTTP request")
        response = requests.get(url, timeout=30)
        response_size = len(response.content)
        status_code = response.status_code

        logger.debug(f"HTTP Response - Status: {status_code}, Size: {response_size} bytes")

        if status_code != 200:
            logger.warning(f"HTTP request failed with status {status_code}")
            return None

        logger.debug("Parsing article content with readability")
        article = parse(response.text)

        # Get title and content
        article_title = article.title or "Sin título"
        article_content = article.text_content or article.content or ""

        title_length = len(article_title)
        content_length = len(article_content)

        logger.debug(f"Article title: '{article_title}' (length: {title_length})")
        logger.debug(f"Article content length: {content_length} chars")

        if not article_content.strip():
            logger.warning("Article content is empty after parsing")
            return None

        # Format content for summarization
        full_content = f"Title: {article_title}\n\nContent: {article_content}"
        total_length = len(full_content)

        logger.info(f"=== ARTICLE HANDLER COMPLETED SUCCESSFULLY ===")
        logger.info(f"Total content length: {total_length} chars")
        logger.debug(f"Content preview: {full_content[:200]}...")

        return full_content

    except requests.exceptions.Timeout:
        logger.error(f"Timeout when fetching article: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error when fetching article {url}: {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"=== ARTICLE HANDLER FAILED ===")
        logger.error(f"Unexpected error processing article {url}: {str(e)}", exc_info=True)
        return None
