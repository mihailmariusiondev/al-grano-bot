import openai
from typing import List, Optional, Dict, Literal
import asyncio
from bot.utils.text_utils import chunk_text
from bot.utils.logger import logger
from bot.prompts.base_prompts import BASE_PROMPTS
from bot.prompts.prompt_modifiers import (
    generate_tone_modifier,
    generate_length_modifier,
    generate_names_modifier,
)
from bot.config import config # Import config para acceder a los nombres de modelo y URLs

# SummaryType Literal, debe coincidir con las claves en ALL_SUMMARY_PROMPTS
SummaryType = Literal[
    "chat",
    "youtube",
    "telegram_video",
    "voice_message",
    "audio_file",
    "quoted_message",
    "web_article",
    "document",
    "video_note"
    # Si OTHER_PROMPTS tuviera entradas, sus claves se listarían aquí también
]

class OpenAIService:
    _instance = None
    # Context length for deepseek/deepseek-r1-0528-qwen3-8b:free is 131K tokens.
    # 1 token ~= 3.5 caracteres (estimación).
    # Max input characters for raw text, before system prompts and reserving space for output.
    # Using a safety margin (e.g., 75% of (total_tokens * chars_per_token)).
    # This leaves 25% for system prompt, user prompt structure, and model output.
    PRIMARY_MODEL_MAX_TOKENS = 131000 # Max tokens for deepseek/deepseek-r1-0528-qwen3-8b:free (input + output)
    CHARS_PER_TOKEN_ESTIMATE = 3.5
    # Calculate max input characters for the primary model, used for chunking
    MAX_INPUT_CHARS_PRIMARY_MODEL = int(PRIMARY_MODEL_MAX_TOKENS * CHARS_PER_TOKEN_ESTIMATE * 0.75)

    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self,
                   openrouter_api_key: str,
                   openai_api_key: str, # Para Whisper
                   openrouter_site_url: str,
                   openrouter_site_name: str):
        if not self.initialized:
            if not openrouter_api_key:
                raise ValueError("OpenRouter API key is required")
            if not openai_api_key:
                raise ValueError("OpenAI API key (for Whisper) is required")
            self.openrouter_client = openai.AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_api_key
            )
            self.openai_client = openai.AsyncOpenAI(
                api_key=openai_api_key
            ) # Cliente para API directa de OpenAI (Whisper)
            self.openrouter_extra_headers = {
                "HTTP-Referer": openrouter_site_url,
                "X-Title": openrouter_site_name,
            }
            self.logger = logger.get_logger("openai_service")
            self.initialized = True
            self.logger.info(f"OpenAIService initialized. OpenRouter Primary Model: {config.OPENROUTER_PRIMARY_MODEL}, Max input chars for chunking: {self.MAX_INPUT_CHARS_PRIMARY_MODEL}")

    async def _execute_chat_completion(
        self,
        client: openai.AsyncOpenAI,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None, # For OpenRouter, this is often model-specific or managed by OR.
                                          # The new primary model's "Max Output Tokens" is not specified (free), fallback is 32K.
        extra_headers: Optional[Dict[str,str]] = None
    ) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")
        try:
            self.logger.debug(f"Making chat completion request with model {model} via {'OpenRouter' if client == self.openrouter_client else 'OpenAI'}")
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_headers=extra_headers if extra_headers else None
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Chat completion failed for model {model}: {e}", exc_info=True)
            # Intentar con fallback si es OpenRouter y el modelo es el primario
            if client == self.openrouter_client and model == config.OPENROUTER_PRIMARY_MODEL and config.OPENROUTER_FALLBACK_MODEL:
                self.logger.warning(f"Primary model {model} failed. Attempting fallback to {config.OPENROUTER_FALLBACK_MODEL}")
                try:
                    response = await client.chat.completions.create(
                        model=config.OPENROUTER_FALLBACK_MODEL,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens, # Fallback model deepseek/deepseek-r1-0528-qwen3-8b might have max_output_tokens of 32K.
                                               # If None, OpenRouter/Novita might use this default or another.
                        extra_headers=extra_headers if extra_headers else None
                    )
                    return response.choices[0].message.content
                except Exception as fallback_e:
                    self.logger.error(f"Fallback model {config.OPENROUTER_FALLBACK_MODEL} also failed: {fallback_e}", exc_info=True)
                    raise RuntimeError(f"Failed to process chat completion with primary and fallback models: {str(fallback_e)}") from fallback_e
            raise RuntimeError(f"Failed to process chat completion: {str(e)}") from e

    async def chat_completion_openrouter(
        self,
        messages: List[Dict[str, str]],
        model: str = config.OPENROUTER_PRIMARY_MODEL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        return await self._execute_chat_completion(
            client=self.openrouter_client,
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers=self.openrouter_extra_headers
        )

    async def transcribe_audio(
        self, file_path: str, model: str = "whisper-1", language: Optional[str] = None
    ) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")
        try:
            self.logger.debug(f"Transcribing audio file: {file_path} using OpenAI client")
            with open(file_path, "rb") as audio_file:
                response = await self.openai_client.audio.transcriptions.create(
                    model=model, file=audio_file, language=language
                )
            return response.text
        except Exception as e:
            self.logger.error(f"Audio transcription failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to transcribe audio: {str(e)}") from e

    async def get_summary(self, content: str, summary_type: SummaryType, summary_config: Dict) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")

        # 1. Obtener la plantilla base
        base_template = BASE_PROMPTS.get(summary_type)
        if not base_template:
            raise ValueError(f"Unsupported summary type: {summary_type}")

        # 2. Preparar los posibles modificadores basados en la configuración
        modifiers = {
            "tone_instruction": generate_tone_modifier(summary_config.get('tone', 'neutral')),
            "length_instruction": generate_length_modifier(summary_config.get('length', 'medium')),
            "names_instruction": generate_names_modifier(summary_config.get('include_names', True)),
        }

        # 3. Construir el prompt final rellenando la plantilla
        # Usamos un bucle para reemplazar solo los placeholders que existen en la plantilla.
        # Esto evita errores si una plantilla no tiene un placeholder como {tone_instruction}.
        final_prompt = base_template
        for key, value in modifiers.items():
            placeholder = f"{{{key}}}"
            if placeholder in final_prompt:
                final_prompt = final_prompt.replace(placeholder, value)

        # Limpiar placeholders no utilizados (si los hubiera)
        import re
        final_prompt = re.sub(r'\{[a-z_]+_instruction\}', '', final_prompt)

        # 4. Añadir la instrucción final de idioma
        language_map = {'es': 'Spanish', 'en': 'English', 'fr': 'French', 'pt': 'Portuguese'}
        output_language = language_map.get(summary_config.get('language', 'es'), 'Spanish')
        final_prompt += f"\n\nIMPORTANT: The entire output response must be written in {output_language}."

        self.logger.debug(f"Final System Prompt for type '{summary_type}':\n{final_prompt}")

        # 5. Llamar a la API de OpenAI
        messages = [
            {"role": "system", "content": final_prompt.strip()},
            {"role": "user", "content": content},
        ]

        # Usar el modelo primario por defecto
        model = summary_config.get("model", config.OPENROUTER_PRIMARY_MODEL) # Using the imported config module for the default model

        try:
            return await self.chat_completion_openrouter(messages, model=model)
        except Exception as e:
            self.logger.error(f"Summary generation failed for type {summary_type}: {e}", exc_info=True)
            raise

    async def summarize_large_document(
        self, text: str, language: str = "Spanish"
    ) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")
        try:
            text_length = len(text)
            self.logger.info(
                f"Iniciando procesamiento de documento de {text_length} caracteres"
            )
            # Usar la constante de clase para el límite de caracteres
            if text_length < self.MAX_INPUT_CHARS_PRIMARY_MODEL:
                self.logger.info(
                    f"Documento dentro del límite ({text_length}/{self.MAX_INPUT_CHARS_PRIMARY_MODEL}). "
                    f"Procesando directamente con {config.OPENROUTER_PRIMARY_MODEL}"
                )
                return await self.get_summary(
                    content=text,
                    summary_type="document",
                    summary_config={"language": language, "model": config.OPENROUTER_PRIMARY_MODEL}
                )
            self.logger.info(f"Documento excede el límite ({text_length}/{self.MAX_INPUT_CHARS_PRIMARY_MODEL}). Dividiendo en chunks...")
            # Adjust chunk_size slightly for safety, ensuring system prompt + user content fits
            chunk_processing_size = int(self.MAX_INPUT_CHARS_PRIMARY_MODEL * 0.95)
            chunks = chunk_text(text, chunk_size=chunk_processing_size)
            self.logger.info(f"Documento dividido en {len(chunks)} chunks")
            self.logger.info(
                f"Iniciando procesamiento paralelo de chunks con {config.OPENROUTER_PRIMARY_MODEL} (o fallback si es necesario)"
            )
            tasks = [
                self.get_summary(
                    content=chunk,
                    summary_type="document",
                    summary_config={"language": language, "model": config.OPENROUTER_PRIMARY_MODEL}
                )
                for chunk in chunks
            ]
            self.logger.info("Esperando resultados de todos los chunks...")
            chunk_summaries = await asyncio.gather(*tasks, return_exceptions=True)
            successful_summaries = []
            for i, summary in enumerate(chunk_summaries):
                if isinstance(summary, Exception):
                    self.logger.error(f"Error procesando chunk {i+1}/{len(chunks)}: {summary}")
                else:
                    successful_summaries.append(summary)
            if not successful_summaries:
                self.logger.error("Todos los chunks fallaron al ser procesados.")
                raise RuntimeError("No se pudo procesar ningún chunk del documento.")
            self.logger.info(f"Procesados {len(successful_summaries)} chunks exitosamente de {len(chunks)}")
            if len(successful_summaries) == 1:
                self.logger.info(
                    "Solo un chunk procesado exitosamente (o era un solo chunk), retornando resumen directamente"
                )
                return successful_summaries[0]
            self.logger.info(f"Generando resumen final con {config.OPENROUTER_PRIMARY_MODEL} a partir de {len(successful_summaries)} resúmenes de chunks")
            combined_summaries = "\n\n".join(successful_summaries)
            self.logger.info(
                f"Longitud total de resúmenes combinados: {len(combined_summaries)} caracteres"
            )

            if len(combined_summaries) > self.MAX_INPUT_CHARS_PRIMARY_MODEL:
                self.logger.warning(f"Los resúmenes combinados ({len(combined_summaries)} chars) exceden MAX_INPUT_CHARS ({self.MAX_INPUT_CHARS_PRIMARY_MODEL}). Se enviará tal cual, confiando en que el modelo maneje la longitud o se ajuste MAX_INPUT_CHARS si es necesario en el futuro.")

            final_summary_prompt_content = (
                "Se han procesado varias partes de un documento extenso. "
                "A continuación se presentan los resúmenes de cada parte. "
                "Por favor, crea un resumen final cohesivo y completo que integre la información de todos estos resúmenes parciales, "
                "manteniendo la estructura y el estilo del tipo de resumen 'documento'.\n\n"
                "Resúmenes parciales:\n"
                f"{combined_summaries}"
            )
            final_summary = await self.get_summary(
                content=final_summary_prompt_content,
                summary_type="document",
                summary_config={"language": language, "model": config.OPENROUTER_PRIMARY_MODEL}
            )
            self.logger.info(
                f"Resumen final generado. Longitud: {len(final_summary)} caracteres"
            )
            return final_summary
        except Exception as e:
            self.logger.error(f"Error procesando documento grande: {e}", exc_info=True)
            raise

openai_service = OpenAIService()
