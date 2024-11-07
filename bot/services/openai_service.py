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
                "chat": lambda language: f"""You are an assistant helping friends catch up in a busy chat group. Your goal is to summarize the conversation in bullet-point format, outlining who said what about which topic.
                    Respond immediately with a short and concise summary, capturing key details and significant events.
                    - (IMPORTANT) NEVER reference message IDs (e.g., #360).
                    - The summary should look like bullet points
                    - Mention who said what about which topic
                    - (VERY IMPORTANT) Should be in {language} language""",

                "video": lambda language: f"""You are an assistant summarizing video content. Your goal is to provide a concise summary of the video.
                    - (VERY IMPORTANT) Should be in {language} language""",

                "general": lambda language, content: f"""You are an assistant tasked with summarizing the following message:

                    {content}

                    Provide a concise and relevant summary of the message content, capturing the main points and key details. The summary should be self-contained and make sense without additional context.

                    - (VERY IMPORTANT) The summary should be in {language} language.
                    - Focus solely on the content of the provided message, without making assumptions or adding extra information.
                    - Keep the summary brief and to the point, while still maintaining clarity and coherence."""
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
