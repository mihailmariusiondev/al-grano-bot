import openai
from typing import List, Optional, Dict, Literal
from ..utils.logger import logger

class OpenAIService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self, api_key: str):
        """Initialize the OpenAI service with API key"""
        if not self.initialized:
            if not api_key:
                raise ValueError("OpenAI API key is required")
            self.client = openai.AsyncOpenAI(api_key=api_key)
            self.logger = logger.get_logger("openai_service")
            self.initialized = True

            # System prompts for different summary types
            self.SUMMARY_PROMPTS = {
                "youtube": """You are a YouTube content summarizer specialized in long-form video content. Create a comprehensive summary that captures the essence of the video. Follow these rules:

                1. Length: Aim for 30-40% of original length for detailed coverage
                2. Structure:
                   - Lead with the main topic/thesis
                   - Maintain the video's logical flow
                   - Include key timestamps or sections if mentioned
                3. Content:
                   - Preserve important statistics and data
                   - Include relevant quotes or key statements
                   - Maintain the original tone (educational, news, etc.)
                   - Highlight main arguments or conclusions
                4. Format:
                   "📝 RESUMEN DE VIDEO DE YOUTUBE:

                   📍 TEMA PRINCIPAL:
                   [main topic/thesis]

                   📊 PUNTOS CLAVE:
                   [key points and data]

                   📝 DESARROLLO:
                   [detailed content]

                   🔍 CONCLUSIONES:
                   [main takeaways/conclusions]"
                """,

                "video": """You are a direct video content summarizer. Create a summary that captures both visual and spoken content. Follow these rules:

                1. Length: Aim for 50-60% of original length
                2. Focus:
                   - Capture main message and context
                   - Include relevant visual elements mentioned
                   - Preserve important details and instructions
                3. Content:
                   - Maintain chronological order
                   - Include key demonstrations or actions
                   - Preserve specific instructions if present
                4. Format:
                   "📝 RESUMEN DE VIDEO:
                   [comprehensive summary including context and key points]"
                """,

                "audio": """You are an audio content summarizer. Create a clear summary of spoken content. Follow these rules:

                1. Length: Aim for 50-60% of original length
                2. Focus:
                   - Capture main message and intent
                   - Preserve important context
                   - Include key details and specifics
                3. Content:
                   - Maintain speaker's main points
                   - Include time-sensitive information
                   - Preserve important quotes or statements
                4. Format:
                   "📝 RESUMEN DE AUDIO:
                   [clear summary of the audio content]"
                """,

                "general": """You are a general content summarizer. Create a clear and concise summary that captures the essence of any content. Follow these rules:

                1. Length: Aim for 40-50% of original length
                2. Structure:
                   - Start with the main topic or key message
                   - Organize points logically
                   - Maintain natural flow of information
                3. Content:
                   - Highlight key information and main points
                   - Preserve important context
                   - Include relevant details and examples
                   - Maintain original tone and intent
                4. Format:
                   "📝 RESUMEN:

                   📍 TEMA PRINCIPAL:
                   [main topic/message]

                   📊 PUNTOS IMPORTANTES:
                   [key points in bullet format]

                   📝 DETALLES RELEVANTES:
                   [important details or context]

                   🔍 CONCLUSIÓN:
                   [main takeaway or conclusion]"
                """,

                "web": """You are a web content and article summarizer. Create a comprehensive summary that captures the key information from web pages and articles. Follow these rules:

                1. Length: Aim for 30-40% of original length
                2. Structure:
                   - Begin with article title and source if available
                   - Maintain the article's logical structure
                   - Separate different sections clearly
                3. Content:
                   - Preserve key statistics and data
                   - Include important quotes
                   - Maintain factual accuracy
                   - Highlight main arguments and findings
                   - Include relevant dates and sources
                4. Format:
                   "📝 RESUMEN DE ARTÍCULO WEB:

                   📍 TÍTULO Y FUENTE:
                   [article title and source]

                   📅 FECHA:
                   [publication date if available]

                   📊 PUNTOS PRINCIPALES:
                   [main points in bullet format]

                   📝 DESARROLLO:
                   [detailed content summary]

                   📊 DATOS IMPORTANTES:
                   [key statistics or data]

                   🔍 CONCLUSIONES:
                   [main findings or conclusions]"
                """
            }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
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
        self,
        file_path: str,
        model: str = "whisper-1",
        language: Optional[str] = None
    ) -> str:
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")
        try:
            self.logger.debug(f"Transcribing audio file: {file_path}")
            with open(file_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    language=language
                )
            return response.text
        except Exception as e:
            self.logger.error(f"Audio transcription failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to transcribe audio: {str(e)}") from e

    async def get_summary(
        self,
        content: str,
        summary_type: Literal["chat", "video", "general"],
        language: str = "Spanish"
    ) -> str:
        """Get summary based on content type and language"""
        if not self.initialized:
            raise RuntimeError("OpenAI service not initialized")

        try:
            # Get appropriate prompt based on summary type
            if summary_type == "general":
                prompt = self.SUMMARY_PROMPTS[summary_type](language, content)
            else:
                prompt = self.SUMMARY_PROMPTS[summary_type](language)

            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ]

            response = await self.chat_completion(messages)
            return response

        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate summary: {str(e)}") from e

openai_service = OpenAIService()  # Single instance
