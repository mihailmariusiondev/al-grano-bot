import openai
from typing import List, Optional, Dict, Literal

from bot.utils.text_utils import chunk_text
from bot.utils.logger import logger


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
                "chat": lambda lang, _: f"""You are an assistant helping friends catch up in a busy chat group. Your goal is to summarize the conversation in bullet-point format, outlining who said what about which topic.
                Respond immediately with a short and concise summary, capturing key details and significant events.
                - (IMPORTANT) NEVER reference message IDs (e.g., #360).
                - The summary should look like bullet points
                - Mention who said what about which topic
                - (VERY IMPORTANT) Should be in {lang}""",
                "youtube": lambda lang, _: f"""You are a YouTube video summarizer. Your goal is to provide a comprehensive summary of the video transcript.
                Follow these rules:
                1. Structure:
                   - Lead with the main topic/thesis
                   - Maintain the video's logical flow
                   - Include key timestamps or sections if mentioned
                2. Content:
                   - Preserve important statistics and data
                   - Include relevant quotes or key statements
                   - Maintain the original tone (educational, news, etc.)
                   - Highlight main arguments or conclusions
                3. Format:
                   "📝 RESUMEN DE VIDEO DE YOUTUBE:
                   📍 TEMA PRINCIPAL:
                   [main topic/thesis]
                   📊 PUNTOS CLAVE:
                   [key points and data]
                   📝 DESARROLLO:
                   [detailed content]
                   🔍 CONCLUSIONES:
                   [main takeaways/conclusions]"
                - (VERY IMPORTANT) Should be in {lang}""",
                "telegram_video": lambda lang, _: f"""You are a direct video content summarizer. Create a summary that captures both visual and spoken content. Follow these rules:
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
                - (VERY IMPORTANT) Should be in {lang}""",
                "voice_message": lambda lang, _: f"""You are a voice message summarizer. Create a clear and natural summary of informal voice messages.
                Follow these rules:
                1. Focus:
                   - Capture the speaker's tone and intention
                   - Preserve the casual/informal nature of voice messages
                   - Include emotional context (if excited, worried, etc.)
                2. Content:
                   - Maintain key points and main message
                   - Include any action items or requests
                   - Preserve time-sensitive information
                3. Format:
                   "🎤 RESUMEN DE MENSAJE DE VOZ:
                   📝 CONTEXTO:
                   [mood/tone/context]
                   📍 MENSAJE PRINCIPAL:
                   [main message]
                   ✅ PUNTOS IMPORTANTES:
                   [key points in bullet format]"
                - (VERY IMPORTANT) Should be in {lang}""",
                "audio_file": lambda lang, _: f"""You are an audio file summarizer specialized in formal audio content like podcasts, interviews, or music.
                Follow these rules:
                1. Structure:
                   - Identify the type of audio (podcast, interview, etc.)
                   - Note any distinct sections or segments
                2. Content:
                   - Capture main topics and discussions
                   - Include speaker names if available
                   - Note any musical elements or sound effects if relevant
                3. Format:
                   "🎵 RESUMEN DE ARCHIVO DE AUDIO:
                   📍 TIPO DE AUDIO:
                   [audio type]
                   👥 PARTICIPANTES:
                   [speakers/participants]
                   📝 CONTENIDO:
                   [main content summary]
                   🔍 PUNTOS DESTACADOS:
                   [highlights in bullet points]"
                - (VERY IMPORTANT) Should be in {lang}""",
                "quoted_message": lambda lang, _: f"""You are a message quote summarizer. Your goal is to provide context and summarize quoted messages clearly and concisely.
                Follow these rules:
                1. Focus:
                   - Capture the essential message without losing context
                   - Preserve any references to previous conversations
                   - Maintain the original intent
                2. Format:
                   "💬 RESUMEN DE MENSAJE:
                   📍 PUNTO PRINCIPAL:
                   [main point]
                   📝 CONTEXTO:
                   [relevant context]
                   ✅ DETALLES IMPORTANTES:
                   [important details in bullet points]"
                - (VERY IMPORTANT) Should be in {lang}""",
                "web_article": lambda lang, _: f"""You are a web article summarizer. Create a comprehensive summary that captures the key information from articles.
                Follow these rules:
                1. Structure:
                   - Begin with article title and source
                   - Maintain the article's logical flow
                2. Content:
                   - Preserve key statistics and data
                   - Include important quotes
                   - Highlight main arguments
                3. Format:
                   "📰 RESUMEN DE ARTÍCULO:
                   📍 TÍTULO:
                   [article title]
                   📝 TEMA PRINCIPAL:
                   [main topic]
                   📊 PUNTOS CLAVE:
                   [key points in bullet format]
                   💡 CONCLUSIONES:
                   [main conclusions]"
                - (VERY IMPORTANT) Should be in {lang}""",
                "poll": lambda lang, _: f"""You are a poll summarizer. Summarize the poll question and options clearly.
                Format:
                📊 RESUMEN DE ENCUESTA:
                ❓ Pregunta: [poll question]
                📍 Opciones: [formatted options]
                - (VERY IMPORTANT) Should be in {lang}""",
                "document": lambda lang, _: f"""You are an expert document analyzer. Your task is to:
                    1. Analyze the content thoroughly
                    2. Provide clear and concise summaries
                    3. Extract key information and main points
                    4. Answer questions about the content accurately
                    5. (VERY IMPORTANT) All responses should be in {lang}
                    6. When citing information, include relevant context
                    7. Focus on providing practical and actionable insights""",
            }

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
        summary_type: Literal[
            "chat",
            "youtube",
            "telegram_video",
            "voice_message",
            "audio_file",
            "quoted_message",
            "web_article",
            "poll",
            "document",
        ],
        language: str = "Spanish",
        model: str = "gpt-4o",
    ) -> str:
        """Generate a summary using the specified model"""
        try:
            prompt = self.SUMMARY_PROMPTS[summary_type](language, content)

            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ]

            response = await self.chat_completion(messages, model=model)
            return response

        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}", exc_info=True)
            raise

    async def summarize_large_document(
        self, text: str, language: str = "Spanish"
    ) -> str:
        """Procesa documentos grandes en múltiples pasadas"""
        try:
            chunks = chunk_text(text)

            chunk_summaries = []
            for chunk in chunks:
                summary = await self.get_summary(
                    content=chunk,
                    summary_type="document",
                    language=language,
                    model="gpt-4o-mini",
                )
                chunk_summaries.append(summary)

            if len(chunk_summaries) > 1:
                final_summary = await self.get_summary(
                    content="\n\n".join(chunk_summaries),
                    summary_type="document",
                    language=language,
                    model="gpt-4o",
                )
                return final_summary
            return chunk_summaries[0]
        except Exception as e:
            self.logger.error(f"Error procesando documento grande: {e}")
            raise


openai_service = OpenAIService()  # Single instance
