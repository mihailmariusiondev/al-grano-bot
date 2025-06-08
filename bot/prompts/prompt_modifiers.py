# bot/prompts/prompt_modifiers.py
from typing import Dict

def generate_tone_modifier(tone: str) -> str:
    """Generates the tone instruction string."""
    tones = {
        "neutral": "The summary must have a neutral and objective tone.",
        "informal": "The summary must have a casual and friendly tone.",
        "sarcastic": "The summary must have a sarcastic and witty tone, subtly mocking the conversation's absurdities.",
        "ironic": "The summary must have a clever, ironic tone, pointing out contradictions or hidden meanings.",
        "absurd": "The summary must have a surreal and absurd tone, using strange metaphors or comparisons."
    }
    return tones.get(tone, tones["neutral"])

def generate_length_modifier(length: str) -> str:
    """Generates the length instruction string."""
    lengths = {
        "short": "The summary should be very concise, limited to 2-3 sentences.",
        "medium": "The summary should be of medium length, around 5-7 sentences.",
        "long": "The summary should be detailed and comprehensive, around 10-15 sentences."
    }
    return lengths.get(length, lengths["medium"])

def generate_names_modifier(include_names: bool) -> str:
    """Generates the participant name instruction string."""
    if include_names:
        return "You must include the names of the participants when attributing points or statements."
    else:
        return "You must not mention any specific participant names; keep the summary anonymous."

def generate_chat_modifiers(config: Dict) -> str:
    """
    Assembles all relevant modifiers for a chat summary based on the config.
    """
    tone = config.get('tone', 'neutral')
    length = config.get('length', 'medium')
    include_names = config.get('include_names', True)

    modifiers = [
        "\n--- Additional Instructions ---",
        generate_tone_modifier(tone),
        generate_length_modifier(length),
        generate_names_modifier(include_names),
        "Use appropriate emojis to make the summary more visual and engaging.",
        "Structure the information clearly, using bullet points or short paragraphs for readability.",
        "NEVER reference message IDs (e.g., #360)."
    ]
    return "\n".join(modifiers)
