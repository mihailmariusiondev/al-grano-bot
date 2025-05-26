# bot/prompts/__init__.py
from typing import Dict, Callable
from .chat_prompts import CHAT_PROMPTS
from .multimedia_prompts import MULTIMEDIA_PROMPTS
from .textual_content_prompts import TEXTUAL_CONTENT_PROMPTS
from .other_prompts import OTHER_PROMPTS # Will be empty if no "other" prompts are active

ALL_SUMMARY_PROMPTS: Dict[str, Callable[[str, str], str]] = {}
ALL_SUMMARY_PROMPTS.update(CHAT_PROMPTS)
ALL_SUMMARY_PROMPTS.update(MULTIMEDIA_PROMPTS)
ALL_SUMMARY_PROMPTS.update(TEXTUAL_CONTENT_PROMPTS)
ALL_SUMMARY_PROMPTS.update(OTHER_PROMPTS)

__all__ = ["ALL_SUMMARY_PROMPTS"]
