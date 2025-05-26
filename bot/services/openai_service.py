import openai
from typing import List, Optional, Dict, Literal, Callable
import asyncio
from bot.utils.text_utils import chunk_text
from bot.utils.logger import logger
from bot.prompts import ALL_SUMMARY_PROMPTS
from bot.config import config # Import config para acceder a los nombres de modelo y URLs

# SummaryType Literal, debe coincidir con las claves en ALL_SUMMARY_PROMPTS
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
    # Si OTHER_PROMPTS tuviera entradas, sus claves se listarían aquí también
]

class OpenAIService:
    _instance = None
    # Ajustar MAX_CONTEXT_CHARS basado en los 164K tokens de DeepSeek R1.
    # 1 token ~= 4 caracteres (estimación). 164,000 tokens * 4 chars/token = 656,000 caracteres.
    # Usar un margen de seguridad (ej. 75-80% del máximo teórico para entrada + salida + prompts).
    # 656,000 * 0.75 = 492,000 caracteres.
    # Este es el límite para la entrada de texto crudo antes de que se añadan los prompts del sistema/usuario.
    DEEPSEEK_R1_MAX_TOKENS = 164000 # Total tokens (input + output)
    CHARS_PER_TOKEN_ESTIMATE = 3.5 # Ajustar según observación, 4 es conservador
    MAX_INPUT_CHARS_PRIMARY_MODEL = int(DEEPSEEK_R1_MAX_TOKENS * CHARS_PER_TOKEN_ESTIMATE * 0.75)


    def __new__(cls):
        if cls._instance is None:
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
            self.logger.info(f"OpenAIService initialized. OpenRouter Primary Model: {config.OPENROUTER_PRIMARY_MODEL}, Max input chars: {self.MAX_INPUT_CHARS_PRIMARY_MODEL}")


    async def _execute_chat_completion(
        self,
        client: openai.AsyncOpenAI,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
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
                max_tokens=max_tokens, # OpenRouter puede ignorar esto o tener su propio límite por modelo
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
                        model=config.OPENROUTER_FALLBACK_MODEL, # Usa el modelo de fallback
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
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
        model: str = config.OPENROUTER_PRIMARY_MODEL, # Usa el modelo primario por defecto
        temperature: float = 0.7,
        max_tokens: Optional[int] = None, # DeepSeek R1 tiene un context length de 164K, pero la salida puede ser menor.
                                          # Dejar a OpenRouter gestionar esto a menos que se necesite un control específico.
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
                response = await self.openai_client.audio.transcriptions.create( # Usa self.openai_client
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
        model: str = config.OPENROUTER_PRIMARY_MODEL, # Usa el modelo primario por defecto
    ) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")
        try:
            prompt_function: Optional[Callable[[str, str], str]] = ALL_SUMMARY_PROMPTS.get(summary_type)
            if prompt_function is None:
                self.logger.error(f"Invalid summary_type or no prompt function found: {summary_type}")
                raise ValueError(f"Unsupported summary type: {summary_type}")

            system_prompt_string = prompt_function(language, content) # 'content' aquí es un placeholder para la firma

            messages = [
                {"role": "system", "content": system_prompt_string},
                {"role": "user", "content": content}, # Contenido real para resumir
            ]
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
                    language=language,
                    model=config.OPENROUTER_PRIMARY_MODEL,
                )

            self.logger.info(f"Documento excede el límite ({text_length}/{self.MAX_INPUT_CHARS_PRIMARY_MODEL}). Dividiendo en chunks...")
            chunks = chunk_text(text, chunk_size=int(self.MAX_INPUT_CHARS_PRIMARY_MODEL * 0.9)) # Un poco menos para cada chunk

            self.logger.info(f"Documento dividido en {len(chunks)} chunks")
            self.logger.info(
                f"Iniciando procesamiento paralelo de chunks con {config.OPENROUTER_PRIMARY_MODEL} (o fallback si es necesario)"
            )

            tasks = [
                self.get_summary(
                    content=chunk,
                    summary_type="document", # Se usa el mismo tipo de prompt, adaptado para resumir partes
                    language=language,
                    model=config.OPENROUTER_PRIMARY_MODEL, # Usar el primario para chunks también, o un modelo más barato/rápido si se configura
                )
                for chunk in chunks
            ]

            self.logger.info("Esperando resultados de todos los chunks...")
            chunk_summaries = await asyncio.gather(*tasks, return_exceptions=True) # Capturar excepciones por chunk

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

            # Si combined_summaries es demasiado largo, truncar o resumir en más pasos.
            # Por ahora, asumimos que cabrá en el modelo final.
            if len(combined_summaries) > self.MAX_INPUT_CHARS_PRIMARY_MODEL:
                self.logger.warning(f"Los resúmenes combinados ({len(combined_summaries)} chars) exceden MAX_INPUT_CHARS ({self.MAX_INPUT_CHARS_PRIMARY_MODEL}). Se truncará o se procesará el texto combinado como un nuevo documento grande si fuera necesario. Por ahora, se envía tal cual.")
                # Aquí se podría implementar una lógica recursiva si es necesario.
                # Por simplicidad, se pasa tal cual y se confía en que el modelo lo maneje o se ajuste MAX_INPUT_CHARS.

            final_summary_prompt_content = (
                "Se han procesado varias partes de un documento extenso. "
                "A continuación se presentan los resúmenes de cada parte. "
                "Por favor, crea un resumen final cohesivo y completo que integre la información de todos estos resúmenes parciales, "
                "manteniendo la estructura y el estilo del tipo de resumen 'documento'.\n\n"
                "Resúmenes parciales:\n"
                f"{combined_summaries}"
            )

            final_summary = await self.get_summary(
                content=final_summary_prompt_content, # Usar el contenido con la instrucción para combinar
                summary_type="document", # Usar el prompt de documento para el estilo final
                language=language,
                model=config.OPENROUTER_PRIMARY_MODEL,
            )
            self.logger.info(
                f"Resumen final generado. Longitud: {len(final_summary)} caracteres"
            )
            return final_summary
        except Exception as e:
            self.logger.error(f"Error procesando documento grande: {e}", exc_info=True)
            raise

openai_service = OpenAIService()
