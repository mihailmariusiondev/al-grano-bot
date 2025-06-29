import re
from typing import List

# Regular expressions
YOUTUBE_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(?:embed\/)?(?:v\/)?(?:shorts\/)?(?:live\/)?(?:[\w\-]{11})"
)
ARTICLE_URL_REGEX = re.compile(r"https?:\/\/\S+")

# Message handling
CHUNK_SIZE = 4096  # Maximum characters per message
PAUSE_BETWEEN_CHUNKS = 0.5  # Seconds between message chunks
MAX_RECENT_MESSAGES = 300  # Maximum messages to fetch for summarization

# Export handling
EXPORT_PROGRESS_BATCH_SIZE = 100  # Messages per progress log in export_chat

# File handling
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

# Supported MIME types
SUPPORTED_AUDIO_TYPES: List[str] = [
    "audio/mpeg",
    "audio/mp4",
    "audio/ogg",
    "audio/wav",
    "audio/webm",
    "audio/x-wav",
]

SUPPORTED_VIDEO_TYPES: List[str] = [
    "video/mp4",
    "video/mpeg",
    "video/ogg",
    "video/webm",
    "video/quicktime",
]

SUPPORTED_DOCUMENT_TYPES: List[str] = [
    "text/plain",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]

# Cooldowns and Limits for /summarize
COOLDOWN_TEXT_SIMPLE_SECONDS = 120  # 2 minutes
COOLDOWN_ADVANCED_SECONDS = 600  # 10 minutes
DAILY_LIMIT_ADVANCED_OPS = 5

# Operation Types
OPERATION_TYPE_TEXT_SIMPLE = "text_simple"
OPERATION_TYPE_ADVANCED = "advanced"

# Message Strings for Limits
MSG_DAILY_LIMIT_REACHED = "Has alcanzado el límite diario de {limit} operaciones avanzadas. Inténtalo de nuevo mañana, figura."
MSG_COOLDOWN_ACTIVE = (
    "Machooo, espérate un poco antes de volver a usar el comando ({remaining}s)."
)


# Localization Labels for Configuration Interface
LABELS = {
    "es": {
        # Main configuration menu
        "title_main": "⚙️ Configuración actual de resúmenes para este chat:",
        "tone_button": "🧠 Tono",
        "length_button": "📏 Longitud",
        "language_button": "🌐 Idioma",
        "names_button": "👥 Incluir nombres",
        "hour_button": "⏰ Hora resumen diario",
        # Current settings labels
        "tone_label": "Tono",
        "length_label": "Longitud",
        "language_label": "Idioma",
        "names_label": "Incluir nombres",
        "hour_label": "Hora resumen diario",
        # Submenu titles
        "tone_submenu_title": "🧠 Selecciona el tono para los resúmenes:",
        "length_submenu_title": "📏 Selecciona la longitud de los resúmenes:",
        "language_submenu_title": "🌐 Selecciona el idioma para los resúmenes:",
        "include_names_submenu_title": "👥 ¿Incluir nombres de participantes?",
        "daily_summary_hour_submenu_title": "⏰ Selecciona la hora para el resumen diario:",
        # Button options
        "buttons": {
            "tone": {
                "neutral": "Neutral 🧾",
                "informal": "Informal 🙂",
                "sarcastic": "Sarcástico 😈",
                "colega": "Colega 🗣️",
                "ironic": "Irónico 🙃",
                "absurd": "Absurdo 🤪",
                "macarra": "Macarra 🥊",
                "cuñao": "Cuñao de Bar 🍻",
                "hijoputesco": "Hijoputesco 😈",
                "misantropo": "Misántropo 🧨",
                "cruel": "Cruelmente Honesto 🔪",
                "chismoso": "Chismoso 🐍",
                "sitcom": "Sitcom Cutre 📺",
                "cinico": "Cínico Quemado 🖕",
                "observador": "Observador 👁️",
                "illuminati": "Cuñao Illuminati 👽",
                "sociopata": "Sociópata 😬",
                "psicologo": "Psicólogo Loco 🧠💣",
                "dios": "Dios da y quita 💀",
                "roast": "Roast Máximo 🔥",
                "cigala": "El Cigala 🎤",
                "kiko": "Kiko Rivera 👑",
                "dioni": "El Dioni 🚐",
                "risitas": "El Risitas 😂",
                "mairena": "Carmen de Mairena 💃",
                "beni": "El Beni 🌊",
                "quico": "Quico Morancos 🎭",
                "ignatius": "Ignatius Farray 🗯️",
                "broncano": "David Broncano 🎙️",
                "veneno": "La Veneno 💅",
                "gitano": "Gitano Vacilón 💃",
                "choni": "La Choni 💎",
                "cani": "Cani de Polígono 🏘️",
                "camello": "Camello de Confianza 💊",
                "payo": "Payo Flipao 🤡",
                "viejuna": "Viejuna del Bar 👵",
                "yonki": "Yonki Zen 🧘‍♂️",
                "chulo": "Chulo de Barrio 😎",
                "elizabethan": "Isabelino 📜",
                "gork": "Gork 🐸",
            },
            "length": {"short": "Corto 📝", "medium": "Medio 📄", "long": "Largo 📋"},
            "language": {
                "es": "Español 🇪🇸",
                "en": "English 🇺🇸",
                "fr": "Français 🇫🇷",
                "pt": "Português 🇧🇷",
            },
            "include_names": {
                "true": "Sí, incluir nombres 👥",
                "false": "No incluir nombres 🚫",
            },
            "daily_summary_hour": {
                "off": "Desactivado ❌",
                "00": "00:00 (Medianoche) 🌙",
                "03": "03:00 (Madrugada) 🌃",
                "08": "08:00 (Mañana) 🌅",
                "12": "12:00 (Mediodía) ☀️",
                "18": "18:00 (Tarde) 🌆",
                "21": "21:00 (Noche) 🌙",
            },
        },
        # Navigation
        "back_button": "⬅️ Volver",
        # Confirmation messages
        "confirm_tone": "Tono actualizado a:",
        "confirm_length": "Longitud actualizada a:",
        "confirm_language": "Idioma actualizado a:",
        "confirm_include_names": "Incluir nombres actualizado a:",
        "confirm_daily_off": "Resumen diario desactivado",
        "confirm_daily_hour": "Resumen diario programado para las",
        # Error messages
        "error_db": "Error al actualizar la configuración. Inténtalo de nuevo.",
        "invalid_option": "Opción no válida.",
        "not_admin": "Solo los administradores pueden cambiar la configuración del chat.",
    },
    "en": {
        # Main configuration menu
        "title_main": "⚙️ Current summary configuration for this chat:",
        "tone_button": "🧠 Tone",
        "length_button": "📏 Length",
        "language_button": "🌐 Language",
        "names_button": "👥 Include names",
        "hour_button": "⏰ Daily summary hour",
        # Current settings labels
        "tone_label": "Tone",
        "length_label": "Length",
        "language_label": "Language",
        "names_label": "Include names",
        "hour_label": "Daily summary hour",
        # Submenu titles
        "tone_submenu_title": "🧠 Select the tone for summaries:",
        "length_submenu_title": "📏 Select the length of summaries:",
        "language_submenu_title": "🌐 Select the language for summaries:",
        "include_names_submenu_title": "👥 Include participant names?",
        "daily_summary_hour_submenu_title": "⏰ Select the hour for daily summary:",
        # Button options
        "buttons": {
            "tone": {
                "neutral": "Neutral 🧾",
                "informal": "Informal 🙂",
                "sarcastic": "Sarcastic 😈",
                "colega": "Buddy 🗣️",
                "ironic": "Ironic 🙃",
                "absurd": "Absurd 🤪",
                "macarra": "Street Tough 🥊",
                "cuñao": "Bar Know-it-all 🍻",
                "hijoputesco": "Sneaky Bastard 😈",
                "misantropo": "Existential Misanthrope 🧨",
                "cruel": "Brutally Honest 🔪",
                "chismoso": "Gossipy Snake 🐍",
                "sitcom": "Cheesy Sitcom 📺",
                "cinico": "Burnt Out Cynic 🖕",
                "observador": "Sharp Observer 👁️",
                "illuminati": "Conspiracy Uncle 👽",
                "sociopata": "Charming Sociopath 😬",
                "psicologo": "Mad Psychologist 🧠💣",
                "dios": "God Gives & Takes 💀",
                "roast": "Maximum Roast 🔥",
                "cigala": "El Cigala Style 🎤",
                "kiko": "Kiko Rivera 👑",
                "dioni": "El Dioni 🚐",
                "risitas": "El Risitas 😂",
                "mairena": "Carmen de Mairena 💃",
                "beni": "El Beni 🌊",
                "quico": "Quico Morancos 🎭",
                "ignatius": "Ignatius Farray 🗯️",
                "broncano": "David Broncano 🎙️",
                "veneno": "La Veneno 💅",
                "gitano": "Gypsy Joker 💃",
                "choni": "La Choni 💎",
                "cani": "Hood Gangster 🏘️",
                "camello": "Trusted Dealer 💊",
                "payo": "Wannabe Gypsy 🤡",
                "viejuna": "Old Bar Lady 👵",
                "yonki": "Zen Junkie 🧘‍♂️",
                "chulo": "Neighborhood Pimp 😎",
                "elizabethan": "Elizabethan 📜",
                "gork": "Gork 🐸",
            },
            "length": {"short": "Short 📝", "medium": "Medium 📄", "long": "Long 📋"},
            "language": {
                "es": "Español 🇪🇸",
                "en": "English 🇺🇸",
                "fr": "Français 🇫🇷",
                "pt": "Português 🇧🇷",
            },
            "include_names": {
                "true": "Yes, include names 👥",
                "false": "Don't include names 🚫",
            },
            "daily_summary_hour": {
                "off": "Disabled ❌",
                "00": "00:00 (Midnight) 🌙",
                "03": "03:00 (Early morning) 🌃",
                "08": "08:00 (Morning) 🌅",
                "12": "12:00 (Noon) ☀️",
                "18": "18:00 (Evening) 🌆",
                "21": "21:00 (Night) 🌙",
            },
        },
        # Navigation
        "back_button": "⬅️ Back",
        # Confirmation messages
        "confirm_tone": "Tone updated to:",
        "confirm_length": "Length updated to:",
        "confirm_language": "Language updated to:",
        "confirm_include_names": "Include names updated to:",
        "confirm_daily_off": "Daily summary disabled",
        "confirm_daily_hour": "Daily summary scheduled for",
        # Error messages
        "error_db": "Error updating configuration. Please try again.",
        "invalid_option": "Invalid option.",
        "not_admin": "Only administrators can change chat configuration.",
    },
    "fr": {
        # Main configuration menu
        "title_main": "⚙️ Configuration actuelle des résumés pour ce chat:",
        "tone_button": "🧠 Ton",
        "length_button": "📏 Longueur",
        "language_button": "🌐 Langue",
        "names_button": "👥 Inclure noms",
        "hour_button": "⏰ Heure résumé quotidien",
        # Current settings labels
        "tone_label": "Ton",
        "length_label": "Longueur",
        "language_label": "Langue",
        "names_label": "Inclure noms",
        "hour_label": "Heure résumé quotidien",
        # Submenu titles
        "tone_submenu_title": "🧠 Sélectionnez le ton pour les résumés:",
        "length_submenu_title": "📏 Sélectionnez la longueur des résumés:",
        "language_submenu_title": "🌐 Sélectionnez la langue pour les résumés:",
        "include_names_submenu_title": "👥 Inclure les noms des participants?",
        "daily_summary_hour_submenu_title": "⏰ Sélectionnez l'heure pour le résumé quotidien:",
        # Button options
        "buttons": {
            "tone": {
                "neutral": "Neutre 🧾",
                "informal": "Informel 🙂",
                "sarcastic": "Sarcastique 😈",
                "colega": "Pote 🗣️",
                "ironic": "Ironique 🙃",
                "absurd": "Absurde 🤪",
                "macarra": "Voyou de Rue 🥊",
                "cuñao": "Monsieur Je-sais-tout 🍻",
                "hijoputesco": "Salaud Sournois 😈",
                "misantropo": "Misanthrope 🧨",
                "cruel": "Brutalement Honnête 🔪",
                "chismoso": "Serpent Bavard 🐍",
                "sitcom": "Sitcom Ringarde 📺",
                "cinico": "Cynique Blasé 🖕",
                "observador": "Observateur Acéré 👁️",
                "illuminati": "Oncle Complot 👽",
                "sociopata": "Sociopathe Charmant 😬",
                "psicologo": "Psy Fou 🧠💣",
                "dios": "Dieu Donne & Reprend 💀",
                "roast": "Roast Maximum 🔥",
                "cigala": "Style El Cigala 🎤",
                "kiko": "Kiko Rivera 👑",
                "dioni": "El Dioni 🚐",
                "risitas": "El Risitas 😂",
                "mairena": "Carmen de Mairena 💃",
                "beni": "El Beni 🌊",
                "quico": "Quico Morancos 🎭",
                "ignatius": "Ignatius Farray 🗯️",
                "broncano": "David Broncano 🎙️",
                "veneno": "La Veneno 💅",
                "gitano": "Gitan Blagueur 💃",
                "choni": "La Choni 💎",
                "cani": "Racaille de Cité 🏘️",
                "camello": "Dealer de Confiance 💊",
                "payo": "Wannabe Gitan 🤡",
                "viejuna": "Vieille du Bar 👵",
                "yonki": "Junkie Zen 🧘‍♂️",
                "chulo": "Proxénète du Quartier 😎",
                "elizabethan": "Élisabéthain 📜",
                "gork": "Gork 🐸",
            },
            "length": {"short": "Court 📝", "medium": "Moyen 📄", "long": "Long 📋"},
            "language": {
                "es": "Español 🇪🇸",
                "en": "English 🇺🇸",
                "fr": "Français 🇫🇷",
                "pt": "Português 🇧🇷",
            },
            "include_names": {
                "true": "Oui, inclure noms 👥",
                "false": "Ne pas inclure noms 🚫",
            },
            "daily_summary_hour": {
                "off": "Désactivé ❌",
                "00": "00:00 (Minuit) 🌙",
                "03": "03:00 (Tôt matin) 🌃",
                "08": "08:00 (Matin) 🌅",
                "12": "12:00 (Midi) ☀️",
                "18": "18:00 (Soir) 🌆",
                "21": "21:00 (Nuit) 🌙",
            },
        },
        # Navigation
        "back_button": "⬅️ Retour",
        # Confirmation messages
        "confirm_tone": "Ton mis à jour:",
        "confirm_length": "Longueur mise à jour:",
        "confirm_language": "Langue mise à jour:",
        "confirm_include_names": "Inclure noms mis à jour:",
        "confirm_daily_off": "Résumé quotidien désactivé",
        "confirm_daily_hour": "Résumé quotidien programmé pour",
        # Error messages
        "error_db": "Erreur lors de la mise à jour. Veuillez réessayer.",
        "invalid_option": "Option invalide.",
        "not_admin": "Seuls les administrateurs peuvent modifier la configuration.",
    },
    "pt": {
        # Main configuration menu
        "title_main": "⚙️ Configuração atual de resumos para este chat:",
        "tone_button": "🧠 Tom",
        "length_button": "📏 Comprimento",
        "language_button": "🌐 Idioma",
        "names_button": "👥 Incluir nomes",
        "hour_button": "⏰ Hora resumo diário",
        # Current settings labels
        "tone_label": "Tom",
        "length_label": "Comprimento",
        "language_label": "Idioma",
        "names_label": "Incluir nomes",
        "hour_label": "Hora resumo diário",
        # Submenu titles
        "tone_submenu_title": "🧠 Selecione o tom para os resumos:",
        "length_submenu_title": "📏 Selecione o comprimento dos resumos:",
        "language_submenu_title": "🌐 Selecione o idioma para os resumos:",
        "include_names_submenu_title": "👥 Incluir nomes dos participantes?",
        "daily_summary_hour_submenu_title": "⏰ Selecione a hora para o resumo diário:",
        # Button options
        "buttons": {
            "tone": {
                "neutral": "Neutro 🧾",
                "informal": "Informal 🙂",
                "sarcastic": "Sarcástico 😈",
                "colega": "Colega 🗣️",
                "ironic": "Irônico 🙃",
                "absurd": "Absurdo 🤪",
                "macarra": "Malandro da Rua 🥊",
                "cuñao": "Sabichão do Bar 🍻",
                "hijoputesco": "Filho da Puta 😈",
                "misantropo": "Misantropo 🧨",
                "cruel": "Brutalmente Honesto 🔪",
                "chismoso": "Fofoqueiro 🐍",
                "sitcom": "Sitcom Brega 📺",
                "cinico": "Cínico Queimado 🖕",
                "observador": "Observador Afiado 👁️",
                "illuminati": "Tio Conspiração 👽",
                "sociopata": "Sociopata Charmoso 😬",
                "psicologo": "Psicólogo Louco 🧠💣",
                "dios": "Deus Dá e Tira 💀",
                "roast": "Roast Máximo 🔥",
                "cigala": "Estilo El Cigala 🎤",
                "kiko": "Kiko Rivera 👑",
                "dioni": "El Dioni 🚐",
                "risitas": "El Risitas 😂",
                "mairena": "Carmen de Mairena 💃",
                "beni": "El Beni 🌊",
                "quico": "Quico Morancos 🎭",
                "ignatius": "Ignatius Farray 🗯️",
                "broncano": "David Broncano 🎙️",
                "veneno": "La Veneno 💅",
                "gitano": "Cigano Brincalhão 💃",
                "choni": "La Choni 💎",
                "cani": "Cani da Periferia 🏘️",
                "camello": "Dealer de Confiança 💊",
                "payo": "Payo Doido 🤡",
                "viejuna": "Velha do Bar 👵",
                "yonki": "Junkie Zen 🧘‍♂️",
                "chulo": "Cafetão do Bairro 😎",
                "elizabethan": "Isabelino 📜",
                "gork": "Gork 🐸",
            },
            "length": {"short": "Curto 📝", "medium": "Médio 📄", "long": "Longo 📋"},
            "language": {
                "es": "Español 🇪🇸",
                "en": "English 🇺🇸",
                "fr": "Français 🇫🇷",
                "pt": "Português 🇧🇷",
            },
            "include_names": {
                "true": "Sim, incluir nomes 👥",
                "false": "Não incluir nomes 🚫",
            },
            "daily_summary_hour": {
                "off": "Desativado ❌",
                "00": "00:00 (Meia-noite) 🌙",
                "03": "03:00 (Madrugada) 🌃",
                "08": "08:00 (Manhã) 🌅",
                "12": "12:00 (Meio-dia) ☀️",
                "18": "18:00 (Tarde) 🌆",
                "21": "21:00 (Noite) 🌙",
            },
        },
        # Navigation
        "back_button": "⬅️ Voltar",
        # Confirmation messages
        "confirm_tone": "Tom atualizado para:",
        "confirm_length": "Comprimento atualizado para:",
        "confirm_language": "Idioma atualizado para:",
        "confirm_include_names": "Incluir nomes atualizado para:",
        "confirm_daily_off": "Resumo diário desativado",
        "confirm_daily_hour": "Resumo diário agendado para",
        # Error messages
        "error_db": "Erro ao atualizar configuração. Tente novamente.",
        "invalid_option": "Opção inválida.",
        "not_admin": "Apenas administradores podem alterar a configuração do chat.",
    },
}


def get_label(key: str, language: str = "es") -> str:
    """Get a label in the specified language.

    Args:
        key: The label key (e.g., 'title_main', 'tone_button')
        language: The language code ('es', 'en', 'fr', 'pt')

    Returns:
        The label text in the specified language, or the Spanish version as fallback
    """
    if language in LABELS and key in LABELS[language]:
        return LABELS[language][key]
    elif key in LABELS["es"]:
        # Fallback to Spanish if language not found
        return LABELS["es"][key]
    else:
        # Return the key itself if not found anywhere
        return key


def get_button_label(category: str, value: str, language: str = "es") -> str:
    """Get a button label for a specific option.

    Args:
        category: The button category ('tone', 'length', 'language', 'include_names', 'daily_summary_hour')
        value: The specific value within the category
        language: The language code ('es', 'en', 'fr', 'pt')

    Returns:
        The button label text in the specified language, or fallback
    """
    if (
        language in LABELS
        and "buttons" in LABELS[language]
        and category in LABELS[language]["buttons"]
        and value in LABELS[language]["buttons"][category]
    ):
        return LABELS[language]["buttons"][category][value]
    elif (
        "buttons" in LABELS["es"]
        and category in LABELS["es"]["buttons"]
        and value in LABELS["es"]["buttons"][category]
    ):
        # Fallback to Spanish
        return LABELS["es"]["buttons"][category][value]
    else:
        # If no label is found and it's an hour, format it properly
        if category == "daily_summary_hour" and value.isdigit():
            return f"{value}:00"
        # Return the value itself if not found
        return value

# Emojis para los tonos
TONE_EMOJIS = {
    "neutral": "🧾",
    "informal": "🙂",
    "sarcastic": "😈",
    "colega": "🗣️",
    "ironic": "🙃",
    "absurd": "��",
    "macarra": "��",
    "cuñao": "🍻",
    "hijoputesco": "😈",
    "misantropo": "🧨",
    "cruel": "🔪",
    "chismoso": "🐍",
    "sitcom": "📺",
    "cinico": "🖕",
    "observador": "👁️",
    "illuminati": "👽",
    "sociopata": "😬",
    "psicologo": "🧠💣",
    "dios": "💀",
    "roast": "🔥",
    "cigala": "🎤",
    "kiko": "👑",
    "dioni": "🚐",
    "risitas": "😂",
    "mairena": "💃",
    "beni": "🌊",
    "quico": "🎭",
    "ignatius": "🗯️",
    "broncano": "🎙️",
    "veneno": "💅",
    "gitano": "💃",
    "choni": "💎",
    "cani": "🏘️",
    "camello": "💊",
    "payo": "🤡",
    "viejuna": "👵",
    "yonki": "🧘‍♂️",
    "chulo": "😎",
    "elizabethan": "📜",
    "gork": "🐸",
}

# Comandos y descripciones
COMMANDS = {
    "chulo": {"es": "Chulo", "en": "Pimp", "fr": "Maquereau", "pt": "Cafetão"},
    "elizabethan": {"es": "Isabelino", "en": "Elizabethan", "fr": "Élisabéthain", "pt": "Isabelino"},
    "gork": {"es": "Gork", "en": "Gork", "fr": "Gork", "pt": "Gork"},
}
