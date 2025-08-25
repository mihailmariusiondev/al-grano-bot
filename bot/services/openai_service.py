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
from bot.config import config
from bot.constants import FALLBACK_MODELS, RATE_LIMIT_RETRY_DELAY

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
    # Context length for deepseek/deepseek-r1-0528:free is 131K tokens.
    # 1 token ~= 3.5 caracteres (estimación).
    # Max input characters for raw text, before system prompts and reserving space for output.
    # Using a safety margin (e.g., 75% of (total_tokens * chars_per_token)).
    # This leaves 25% for system prompt, user prompt structure, and model output.
    MODEL_MAX_TOKENS = 131000 # Max tokens for deepseek/deepseek-r1-0528:free (input + output)
    CHARS_PER_TOKEN_ESTIMATE = 3.5
    # Calculate max input characters for the model, used for chunking
    MAX_INPUT_CHARS_MODEL = int(MODEL_MAX_TOKENS * CHARS_PER_TOKEN_ESTIMATE * 0.75)

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
            self.logger.info(f"OpenAIService initialized. OpenRouter Model: {config.OPENROUTER_MODEL}, Max input chars for chunking: {self.MAX_INPUT_CHARS_MODEL}")

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

        # Calculate approximate token count for logging
        total_chars = sum(len(msg.get('content', '')) for msg in messages)
        estimated_tokens = int(total_chars / self.CHARS_PER_TOKEN_ESTIMATE)

        self.logger.debug(f"=== CHAT COMPLETION REQUEST ===")
        self.logger.debug(f"Model: {model}")
        self.logger.debug(f"Client: {'OpenRouter' if client == self.openrouter_client else 'OpenAI'}")
        self.logger.debug(f"Temperature: {temperature}")
        self.logger.debug(f"Max tokens: {max_tokens}")
        self.logger.debug(f"Messages count: {len(messages)}")
        self.logger.debug(f"Total content chars: {total_chars}")
        self.logger.debug(f"Estimated input tokens: {estimated_tokens}")
        self.logger.debug(f"System prompt length: {len(messages[0]['content']) if messages and messages[0]['role'] == 'system' else 0}")

        # Log complete message content for debugging
        self.logger.debug(f"=== COMPLETE MESSAGES PAYLOAD ===")
        for i, message in enumerate(messages):
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            self.logger.debug(f"Message {i+1} [{role}]: {content}")
        self.logger.debug(f"=== END MESSAGES PAYLOAD ===")

        # Log extra headers if present
        if extra_headers:
            self.logger.debug(f"Extra headers: {extra_headers}")

        try:
            self.logger.info(f"Sending chat completion request to {model}")
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_headers=extra_headers if extra_headers else None
            )

            response_content = response.choices[0].message.content
            response_length = len(response_content) if response_content else 0
            estimated_response_tokens = int(response_length / self.CHARS_PER_TOKEN_ESTIMATE)

            self.logger.debug(f"=== CHAT COMPLETION RESPONSE ===")
            self.logger.debug(f"Response length: {response_length} chars")
            self.logger.debug(f"Estimated response tokens: {estimated_response_tokens}")
            self.logger.debug(f"Total estimated tokens used: {estimated_tokens + estimated_response_tokens}")

            # Log complete response content for debugging
            self.logger.debug(f"=== COMPLETE RESPONSE CONTENT ===")
            self.logger.debug(f"Response: {response_content}")
            self.logger.debug(f"=== END RESPONSE CONTENT ===")

            # Log usage info if available
            if hasattr(response, 'usage') and response.usage:
                self.logger.info(f"Token usage - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}, Total: {response.usage.total_tokens}")

            self.logger.info(f"Chat completion successful with model {model}")
            return response_content
        except Exception as e:
            self.logger.error(f"Chat completion failed for model {model}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to process chat completion: {str(e)}") from e

    async def chat_completion_openrouter(
        self,
        messages: List[Dict[str, str]],
        model: str = config.OPENROUTER_MODEL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        return await self._chat_completion_with_fallback(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    async def _chat_completion_with_fallback(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Chat completion with automatic fallback on rate limits"""
        
        # Start with requested model, then try fallback models
        models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]
        
        last_exception = None
        
        for i, current_model in enumerate(models_to_try):
            try:
                self.logger.info(f"Attempting model {i+1}/{len(models_to_try)}: {current_model}")
                
                result = await self._execute_chat_completion(
                    client=self.openrouter_client,
                    messages=messages,
                    model=current_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers=self.openrouter_extra_headers
                )
                
                if i > 0:  # Used fallback
                    self.logger.info(f"✅ Fallback successful with model: {current_model}")
                
                return result
                
            except Exception as e:
                error_msg = str(e).lower()
                last_exception = e
                
                # Check if it's a rate limit error (429)
                if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg:
                    self.logger.warning(f"⚠️ Rate limit hit for {current_model}: {e}")
                    
                    if i < len(models_to_try) - 1:  # Not the last model
                        self.logger.info(f"⏳ Waiting {RATE_LIMIT_RETRY_DELAY}s before trying next model...")
                        await asyncio.sleep(RATE_LIMIT_RETRY_DELAY)
                        continue
                else:
                    # Non-rate-limit error, log and continue
                    self.logger.error(f"❌ Model {current_model} failed with non-rate-limit error: {e}")
                    continue
        
        # All models failed
        self.logger.error(f"🚫 ALL {len(models_to_try)} MODELS FAILED. Last error: {last_exception}")
        raise RuntimeError(f"All fallback models exhausted. Last error: {str(last_exception)}") from last_exception

    async def transcribe_audio(
        self, file_path: str, model: str = "whisper-1", language: Optional[str] = None
    ) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")

        self.logger.debug(f"=== AUDIO TRANSCRIPTION STARTED ===")
        self.logger.debug(f"File path: {file_path}")
        self.logger.debug(f"Model: {model}")
        self.logger.debug(f"Language: {language}")

        try:
            # Check file exists and get size
            import os
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Audio file not found: {file_path}")

            file_size = os.path.getsize(file_path)
            self.logger.debug(f"Audio file size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")

            self.logger.info(f"Starting transcription of {file_path} with Whisper")
            with open(file_path, "rb") as audio_file:
                response = await self.openai_client.audio.transcriptions.create(
                    model=model, file=audio_file, language=language
                )

            transcription_text = response.text
            transcription_length = len(transcription_text)

            self.logger.debug(f"=== AUDIO TRANSCRIPTION COMPLETED ===")
            self.logger.debug(f"Transcription length: {transcription_length} chars")
            self.logger.info(f"Audio transcription successful for {file_path}")

            return transcription_text
        except Exception as e:
            self.logger.error(f"Audio transcription failed for {file_path}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to transcribe audio: {str(e)}") from e

    async def get_summary(self, content: str, summary_type: SummaryType, summary_config: Dict) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")

        self.logger.debug(f"=== GET_SUMMARY STARTED ===")
        self.logger.debug(f"Summary type: {summary_type}")
        self.logger.debug(f"Content length: {len(content)} chars")
        self.logger.debug(f"Summary config: {summary_config}")

        # 1. Obtener la plantilla base
        base_template = BASE_PROMPTS.get(summary_type)
        if not base_template:
            self.logger.error(f"No template found for summary type: {summary_type}")
            raise ValueError(f"Unsupported summary type: {summary_type}")

        self.logger.debug(f"Base template length: {len(base_template)} chars")

        # 2. Preparar los posibles modificadores basados en la configuración
        tone = summary_config.get('tone', 'neutral')
        length = summary_config.get('length', 'medium')
        include_names = summary_config.get('include_names', True)
        language = summary_config.get('language', 'es')

        self.logger.debug(f"Modifiers - Tone: {tone}, Length: {length}, Include names: {include_names}, Language: {language}")

        modifiers = {
            "tone_instruction": generate_tone_modifier(tone),
            "length_instruction": generate_length_modifier(length),
            "names_instruction": generate_names_modifier(include_names),
        }

        # 3. Construir el prompt final rellenando la plantilla
        # Usamos un bucle para reemplazar solo los placeholders que existen en la plantilla.
        # Esto evita errores si una plantilla no tiene un placeholder como {tone_instruction}.
        final_prompt = base_template
        replacements_made = 0
        for key, value in modifiers.items():
            placeholder = f"{{{key}}}"
            if placeholder in final_prompt:
                final_prompt = final_prompt.replace(placeholder, value)
                replacements_made += 1
                self.logger.debug(f"Replaced {placeholder} with modifier")

        self.logger.debug(f"Made {replacements_made} placeholder replacements")

        # Limpiar placeholders no utilizados (si los hubiera)
        import re
        unused_placeholders = re.findall(r'\{[a-z_]+_instruction\}', final_prompt)
        if unused_placeholders:
            self.logger.debug(f"Cleaning unused placeholders: {unused_placeholders}")
        final_prompt = re.sub(r'\{[a-z_]+_instruction\}', '', final_prompt)

        # 4. Añadir la instrucción final de idioma
        language_map = {'es': 'Spanish', 'en': 'English', 'fr': 'French', 'pt': 'Portuguese'}
        output_language = language_map.get(language, 'Spanish')
        final_prompt += f"\n\nIMPORTANT: The entire output response must be written in {output_language}."

        self.logger.debug(f"Final prompt length: {len(final_prompt)} chars")
        self.logger.debug(f"Output language set to: {output_language}")

        # 5. Llamar a la API de OpenAI
        messages = [
            {"role": "system", "content": final_prompt.strip()},
            {"role": "user", "content": content},
        ]

        # Usar el modelo primario por defecto con fallback automático
        model = summary_config.get("model", config.OPENROUTER_MODEL)
        self.logger.info(f"Using model: {model} for summary type: {summary_type} (with fallback)")

        try:
            result = await self.chat_completion_openrouter(messages, model=model)
            self.logger.info(f"Summary generation completed successfully for type {summary_type}")
            self.logger.debug(f"Generated summary length: {len(result) if result else 0} chars")
            return result
        except Exception as e:
            self.logger.error(f"Summary generation failed for type {summary_type} (all models): {e}", exc_info=True)
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
            if text_length < self.MAX_INPUT_CHARS_MODEL:
                self.logger.info(
                    f"Documento dentro del límite ({text_length}/{self.MAX_INPUT_CHARS_MODEL}). "
                    f"Procesando directamente con {config.OPENROUTER_MODEL}"
                )
                return await self.get_summary(
                    content=text,
                    summary_type="document",
                    summary_config={"language": language, "model": config.OPENROUTER_MODEL}
                )
            self.logger.info(f"Documento excede el límite ({text_length}/{self.MAX_INPUT_CHARS_MODEL}). Dividiendo en chunks...")
            # Adjust chunk_size slightly for safety, ensuring system prompt + user content fits
            chunk_processing_size = int(self.MAX_INPUT_CHARS_MODEL * 0.95)
            chunks = chunk_text(text, chunk_size=chunk_processing_size)
            self.logger.info(f"Documento dividido en {len(chunks)} chunks")
            self.logger.info(
                f"Iniciando procesamiento paralelo de chunks con {config.OPENROUTER_MODEL}"
            )
            tasks = [
                self.get_summary(
                    content=chunk,
                    summary_type="document",
                    summary_config={"language": language, "model": config.OPENROUTER_MODEL}
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
            self.logger.info(f"Generando resumen final con {config.OPENROUTER_MODEL} a partir de {len(successful_summaries)} resúmenes de chunks")
            combined_summaries = "\n\n".join(successful_summaries)
            self.logger.info(
                f"Longitud total de resúmenes combinados: {len(combined_summaries)} caracteres"
            )

            if len(combined_summaries) > self.MAX_INPUT_CHARS_MODEL:
                self.logger.warning(f"Los resúmenes combinados ({len(combined_summaries)} chars) exceden MAX_INPUT_CHARS ({self.MAX_INPUT_CHARS_MODEL}). Se enviará tal cual, confiando en que el modelo maneje la longitud o se ajuste MAX_INPUT_CHARS si es necesario en el futuro.")

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
                summary_config={"language": language, "model": config.OPENROUTER_MODEL}
            )
            self.logger.info(
                f"Resumen final generado. Longitud: {len(final_summary)} caracteres"
            )
            return final_summary
        except Exception as e:
            self.logger.error(f"Error procesando documento grande: {e}", exc_info=True)
            raise

openai_service = OpenAIService()
