# bot/constants/__init__.py
"""
Constants package for centralized configuration.
"""

from .models import (
    DEFAULT_MODEL,
    FALLBACK_MODELS,
    MODEL_INFO,
    RATE_LIMIT_RETRY_DELAY,
    MAX_FALLBACK_ATTEMPTS
)

__all__ = [
    "DEFAULT_MODEL",
    "FALLBACK_MODELS", 
    "MODEL_INFO",
    "RATE_LIMIT_RETRY_DELAY",
    "MAX_FALLBACK_ATTEMPTS"
]