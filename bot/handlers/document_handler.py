from docx import Document
import PyPDF2
import io
import logging
from typing import Optional
from ..services.openai_service import openai_service

SUPPORTED_DOCUMENT_TYPES = {
    "application/pdf": "pdf",
    "text/plain": "txt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"
}

async def document_handler(message, context) -> Optional[str]:
    """Handle document messages"""
    try:
        document = message.document
        if document.mime_type not in SUPPORTED_DOCUMENT_TYPES:
            raise ValueError(f"Tipo de documento no soportado: {document.mime_type}")

        # Download document
        file = await context.bot.get_file(document.file_id)
        file_bytes = await file.download_as_bytearray()

        # Extract text based on file type
        if document.mime_type == "application/pdf":
            text_content = extract_text_from_pdf(file_bytes)
        elif document.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text_content = extract_text_from_docx(file_bytes)
        else:  # text/plain
            text_content = file_bytes.decode('utf-8')

        # Summarize using the large document processor
        return await openai_service.summarize_large_document(text_content)

    except Exception as e:
        logging.error(f"Error en document handler: {e}")
        raise

def extract_text_from_pdf(file_bytes: bytearray) -> str:
    """Extract text content from PDF file"""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PyPDF2.PdfReader(pdf_file)

        text_content = []
        for page in reader.pages:
            text_content.append(page.extract_text())

        return "\n".join(text_content)
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise

def extract_text_from_docx(file_bytes: bytearray) -> str:
    """Extract text content from DOCX file"""
    try:
        docx_file = io.BytesIO(file_bytes)
        doc = Document(docx_file)

        text_content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # Skip empty paragraphs
                text_content.append(paragraph.text)

        return "\n".join(text_content)
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        raise
