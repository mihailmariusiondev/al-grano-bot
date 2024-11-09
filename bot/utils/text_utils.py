from typing import List


def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """Divide el texto en chunks más pequeños"""
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = []
    current_size = 0

    for paragraph in paragraphs:
        if len(paragraph.strip()) == 0:
            continue

        # Si el párrafo actual excede el tamaño del chunk, dividirlo
        if len(paragraph) > chunk_size:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_size = 0

            # Dividir el párrafo largo en partes más pequeñas
            words = paragraph.split()
            current_part = []
            current_part_size = 0

            for word in words:
                if current_part_size + len(word) > chunk_size:
                    chunks.append(" ".join(current_part))
                    current_part = [word]
                    current_part_size = len(word)
                else:
                    current_part.append(word)
                    current_part_size += len(word) + 1

            if current_part:
                chunks.append(" ".join(current_part))
        else:
            if current_size + len(paragraph) > chunk_size:
                chunks.append("\n".join(current_chunk))
                current_chunk = [paragraph]
                current_size = len(paragraph)
            else:
                current_chunk.append(paragraph)
                current_size += len(paragraph)

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks
