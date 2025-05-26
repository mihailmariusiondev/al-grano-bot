import openai
from typing import List, Optional, Dict, Literal, Callable
import asyncio
from bot.utils.text_utils import chunk_text
from bot.utils.logger import logger
from bot.prompts import ALL_SUMMARY_PROMPTS # New import

# SummaryType Literal, should match keys in ALL_SUMMARY_PROMPTS
SummaryType = Literal[
    "chat_long",
    "chat_short",
    "youtube",
    "telegram_video",
    "voice_message",
    "audio_file",
    "quoted_message",
    "web_article",
    "document",
    "video_note"
    # If OTHER_PROMPTS had entries, their keys would be listed here too
]

class OpenAIService:
    _instance = None
    GPT4O_MAX_TOKENS = 128000
    CHARS_PER_TOKEN = 4
    MAX_INPUT_CHARS = (
        GPT4O_MAX_TOKENS * CHARS_PER_TOKEN * 0.75
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self, api_key: str):
        if not self.initialized:
            if not api_key:
                raise ValueError("OpenAI API key is required")
            self.client = openai.AsyncOpenAI(api_key=api_key)
            self.logger = logger.get_logger("openai_service")
            self.initialized = True
            # The self.SUMMARY_PROMPTS dictionary has been removed from here.
            # Prompts are now accessed via the imported ALL_SUMMARY_PROMPTS.

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")
        try:
            self.logger.debug(f"Making chat completion request with model {model}")
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Chat completion failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to process chat completion: {str(e)}") from e

    async def transcribe_audio(
        self, file_path: str, model: str = "whisper-1", language: Optional[str] = None
    ) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")
        try:
            self.logger.debug(f"Transcribing audio file: {file_path}")
            with open(file_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=model, file=audio_file, language=language
                )
            return response.text
        except Exception as e:
            self.logger.error(f"Audio transcription failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to transcribe audio: {str(e)}") from e

    async def get_summary(
        self,
        content: str,
        summary_type: SummaryType,
        language: str = "Spanish",
        model: str = "gpt-4o",
    ) -> str:
        """Generate a summary using the specified model and externalized prompts."""
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")
        try:
            prompt_function: Optional[Callable[[str, str], str]] = ALL_SUMMARY_PROMPTS.get(summary_type)

            if prompt_function is None:
                self.logger.error(f"Invalid summary_type or no prompt function found: {summary_type}")
                raise ValueError(f"Unsupported summary type: {summary_type}")

            # The prompt_function expects (lang, content_for_signature_match).
            # The `content` argument passed here matches the second parameter of the
            # prompt template function's signature (def template(lang: str, _: str = None)),
            # but it's typically ignored by the template function when generating the system prompt.
            # The actual content to be summarized is passed as the user message.
            system_prompt_string = prompt_function(language, content)

            messages = [
                {"role": "system", "content": system_prompt_string},
                {"role": "user", "content": content}, # Actual content for summarization
            ]
            return await self.chat_completion(messages, model=model)
        except Exception as e:
            self.logger.error(f"Summary generation failed for type {summary_type}: {e}", exc_info=True)
            raise

    async def summarize_large_document(
        self, text: str, language: str = "Spanish"
    ) -> str:
        """Procesa documentos grandes de manera más eficiente usando GPT-4o-mini para chunks"""
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")
        try:
            text_length = len(text)
            self.logger.info(
                f"Iniciando procesamiento de documento de {text_length} caracteres"
            )

            if len(text) < OpenAIService.MAX_INPUT_CHARS:
                self.logger.info(
                    f"Documento dentro del límite ({text_length}/{OpenAIService.MAX_INPUT_CHARS}). "
                    "Procesando directamente con GPT-4o"
                )
                return await self.get_summary(
                    content=text,
                    summary_type="document",
                    language=language,
                    model="gpt-4o",
                )

            self.logger.info("Documento excede el límite. Dividiendo en chunks...")
            chunks = chunk_text(text, chunk_size=int(OpenAIService.MAX_INPUT_CHARS))
            self.logger.info(f"Documento dividido en {len(chunks)} chunks")

            self.logger.info(
                "Iniciando procesamiento paralelo de chunks con GPT-4o-mini"
            )
            tasks = [
                self.get_summary(
                    content=chunk,
                    summary_type="document",
                    language=language,
                    model="gpt-4o-mini",
                )
                for chunk in chunks
            ]
            self.logger.info("Esperando resultados de todos los chunks...")
            chunk_summaries = await asyncio.gather(*tasks)
            self.logger.info(f"Procesados {len(chunk_summaries)} chunks exitosamente")

            if len(chunk_summaries) == 1:
                self.logger.info(
                    "Solo un chunk procesado, retornando resumen directamente"
                )
                return chunk_summaries[0]

            self.logger.info("Generando resumen final con GPT-4o")
            combined_summaries = "\n\n".join(chunk_summaries)
            self.logger.info(
                f"Longitud total de resúmenes combinados: {len(combined_summaries)} caracteres"
            )

            final_summary = await self.get_summary(
                content=combined_summaries,
                summary_type="document",
                language=language,
                model="gpt-4o",
            )
            self.logger.info(
                f"Resumen final generado. Longitud: {len(final_summary)} caracteres"
            )
            return final_summary
        except Exception as e:
            self.logger.error(f"Error procesando documento grande: {e}", exc_info=True)
            raise

openai_service = OpenAIService()
