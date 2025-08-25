# bot/constants/models.py
"""
OpenRouter model constants and fallback configuration.
Centralized model management for better maintainability.
"""

from typing import List, Dict, Any

# Primary model (default)
DEFAULT_MODEL = "deepseek/deepseek-r1-0528:free"

# Fallback models ordered by priority
# Priority: Qwen > Kimi > GLM > Gemini > DeepSeek variants
# NO LLAMA - "llama fuera es una basura"
FALLBACK_MODELS: List[str] = [
    "qwen/qwen3-235b-a22b:free",        # 235B + thinking mode
    "moonshotai/kimi-k2:free",          # Stable and reliable
    "z-ai/glm-4.5-air:free",           # MoE efficient
    "google/gemini-2.0-flash-exp:free", # 1M context window
    "deepseek/deepseek-r1:free",        # Main DeepSeek
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",  # OK pero último
    "deepseek/deepseek-r1-0528:free"    # Original/backup
]

# Model metadata for logging and debugging
MODEL_INFO: Dict[str, Dict[str, Any]] = {
    "qwen/qwen3-235b-a22b:free": {
        "name": "Qwen 3 235B",
        "size": "235B",
        "features": ["thinking", "reasoning"],
        "context": "32K"
    },
    "moonshotai/kimi-k2:free": {
        "name": "Kimi K2", 
        "size": "Unknown",
        "features": ["stable", "reliable"],
        "context": "128K"
    },
    "z-ai/glm-4.5-air:free": {
        "name": "GLM-4.5 Air",
        "size": "MoE",
        "features": ["efficient", "fast"],
        "context": "128K"
    },
    "google/gemini-2.0-flash-exp:free": {
        "name": "Gemini 2.0 Flash",
        "size": "Unknown",
        "features": ["experimental", "long-context"],
        "context": "1M"
    },
    "deepseek/deepseek-r1:free": {
        "name": "DeepSeek R1",
        "size": "Unknown",
        "features": ["reasoning", "thinking"],
        "context": "128K"
    },
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free": {
        "name": "Nemotron Ultra",
        "size": "253B", 
        "features": ["powerful", "last-resort"],
        "context": "128K"
    },
    "deepseek/deepseek-r1-0528:free": {
        "name": "DeepSeek R1 0528", 
        "size": "Unknown",
        "features": ["reasoning", "stable"],
        "context": "131K"
    }
}

# Rate limit handling configuration
RATE_LIMIT_RETRY_DELAY = 1.0  # seconds between model attempts
MAX_FALLBACK_ATTEMPTS = len(FALLBACK_MODELS)  # 7 models total