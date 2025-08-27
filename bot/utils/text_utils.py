from typing import List
import logging
import re


def chunk_text(text: str, chunk_size: int = 384000) -> List[str]:
    """Divide el texto en chunks basados en el límite de tokens de GPT-4o"""
    logger = logging.getLogger(__name__)
    logger.info(
        f"Iniciando división de texto de {len(text)} caracteres en chunks de {chunk_size}"
    )

    # Si el texto es más corto que el chunk_size, retornarlo directamente
    if len(text) <= chunk_size:
        logger.info("Texto dentro del límite, retornando sin dividir")
        return [text]

    chunks = []
    current_chunk = []
    current_size = 0

    # Dividir por párrafos
    paragraphs = text.split("\n")
    logger.info(f"Texto dividido en {len(paragraphs)} párrafos")

    for i, paragraph in enumerate(paragraphs, 1):
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        paragraph_size = len(paragraph)
        logger.debug(
            f"Procesando párrafo {i}/{len(paragraphs)} "
            f"(tamaño: {paragraph_size} caracteres)"
        )

        # Si el párrafo es más grande que el chunk_size, dividirlo
        if paragraph_size > chunk_size:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                logger.debug(f"Chunk completado: {len(chunks[-1])} caracteres")
                current_chunk = []
                current_size = 0

            logger.info(
                f"Párrafo excede tamaño máximo ({paragraph_size} > {chunk_size}). "
                "Dividiendo en oraciones"
            )
            sentences = paragraph.replace(". ", ".\n").split("\n")
            current_sentence_chunk = []
            current_sentence_size = 0

            for sentence in sentences:
                sentence_size = len(sentence)
                if current_sentence_size + sentence_size > chunk_size:
                    chunks.append(" ".join(current_sentence_chunk))
                    logger.debug(
                        f"Chunk de oraciones completado: {len(chunks[-1])} caracteres"
                    )
                    current_sentence_chunk = [sentence]
                    current_sentence_size = sentence_size
                else:
                    current_sentence_chunk.append(sentence)
                    current_sentence_size += sentence_size

            if current_sentence_chunk:
                chunks.append(" ".join(current_sentence_chunk))
                logger.debug(
                    f"Último chunk de oraciones completado: {len(chunks[-1])} caracteres"
                )

        # Si añadir el párrafo excede el tamaño del chunk, crear uno nuevo
        elif current_size + paragraph_size > chunk_size:
            chunks.append("\n".join(current_chunk))
            logger.debug(f"Chunk completado: {len(chunks[-1])} caracteres")
            current_chunk = [paragraph]
            current_size = paragraph_size
        else:
            current_chunk.append(paragraph)
            current_size += paragraph_size

    # Añadir el último chunk si existe
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        logger.debug(f"Último chunk completado: {len(chunks[-1])} caracteres")

    logger.info(
        f"División completada. Generados {len(chunks)} chunks. "
        f"Tamaños: {[len(chunk) for chunk in chunks]}"
    )
    return chunks


def clean_ai_response(text: str) -> str:
    """Clean AI response by removing technical metadata and thinking tags.
    
    This function removes:
    - <think> and </think> tags with their content 
    - <thinking> and </thinking> tags with their content
    - Technical debugging information patterns
    - Sentence count validation patterns
    
    Args:
        text: Raw AI response text
        
    Returns:
        Cleaned text without technical metadata
    """
    # Handle None or empty input
    if text is None:
        return ""
    if not text:
        return text
    
    # Remove <think>...</think> tags and content (case insensitive, only complete pairs)
    text = re.sub(r'<think\s*>.*?</think\s*>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove <thinking>...</thinking> tags and content (case insensitive, only complete pairs) 
    text = re.sub(r'<thinking\s*>.*?</thinking\s*>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up extra whitespace and newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double
    text = text.strip()
    
    return text
