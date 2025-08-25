# bot/constants/messages.py
"""
User-facing messages constants.
All user messages should be friendly and never expose technical errors.
"""

# Success messages
SUCCESS_MESSAGES = {
    "PROCESSING": "⏳ Procesando tu solicitud...",
    "COMPLETED": "✅ Proceso completado exitosamente",
    "SAVED": "💾 Información guardada correctamente"
}

# Generic error messages (user-friendly, never technical)
USER_ERROR_MESSAGES = {
    "GENERAL_ERROR": "🤖 Estoy teniendo dificultades técnicas. Por favor, inténtalo de nuevo en unos momentos.",
    "RATE_LIMIT": "⏰ Estoy un poco ocupado ahora. Inténtalo de nuevo en unos segundos.",
    "PROCESSING_ERROR": "🔄 No pude procesar tu solicitud completamente. Por favor, inténtalo de nuevo.",
    "TIMEOUT_ERROR": "⏱️ La operación está tardando más de lo esperado. Inténtalo de nuevo en unos momentos.",
    "NETWORK_ERROR": "🌐 Problemas de conectividad. Por favor, inténtalo de nuevo.",
    "UNSUPPORTED_CONTENT": "📄 Este tipo de contenido no es compatible actualmente.",
    "SERVICE_UNAVAILABLE": "🔧 El servicio está temporalmente no disponible. Inténtalo más tarde.",
    "INVALID_REQUEST": "❓ No entendí tu solicitud. Usa /help para ver los comandos disponibles.",
    "PERMISSION_ERROR": "🚫 No tienes permisos para realizar esta acción.",
    "FILE_ERROR": "📁 Hubo un problema procesando el archivo. Inténtalo con otro archivo.",
    "CONFIGURATION_ERROR": "⚙️ Hay un problema con la configuración. Usa /configurar_resumen para revisarla.",
}

# Command-specific messages
COMMAND_MESSAGES = {
    "SUMMARIZE": {
        "NO_CONTENT": "📝 No encontré contenido para resumir. Responde a un mensaje o usa el comando en un chat con historial.",
        "PROCESSING": "📄 Generando tu resumen personalizado...",
        "LANGUAGE_ERROR": "🌍 Idioma no soportado. Configura un idioma válido con /configurar_resumen."
    },
    "EXPORT": {
        "PROCESSING": "📦 Preparando la exportación del chat...",
        "NO_MESSAGES": "📭 No hay mensajes para exportar en este chat.",
        "FORMAT_ERROR": "📋 Formato de exportación no válido."
    },
    "CONFIGURE": {
        "SUCCESS": "✅ Configuración actualizada correctamente",
        "INVALID_OPTION": "❌ Opción no válida. Inténtalo de nuevo."
    }
}