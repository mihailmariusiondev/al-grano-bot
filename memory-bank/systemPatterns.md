# System Patterns: Al-Grano Bot

## 1. Arquitectura del Sistema

El "Al-Grano Bot" sigue una arquitectura modular enfocada en la funcionalidad de resumen:

- **Capa de Interfaz (Telegram)**: `TelegramBot` (`bot/bot.py`) gestiona la comunicación con la API de Telegram.
- **Capa de Comandos (`bot/commands/`)**: Contiene manejadores para comandos. El comando `/summarize` es central y contiene lógica compleja para:
  - Identificación del tipo de usuario (admin/gratuito).
  - Clasificación del tipo de operación de resumen (simple/costosa).
  - Aplicación de límites de uso (cooldowns, cuotas diarias) para usuarios gratuitos.
  - Delegación a handlers de contenido específico.
- **Capa de Manejadores de Contenido (`bot/handlers/`)**: Módulos para procesar tipos específicos de contenido para resumen (audio, video, documento, imagen, artículo web, YouTube). Son invocados por el comando `/summarize`. El `message_handler.py` genérico (en `bot/commands/`) guarda mensajes para el contexto de resúmenes de chat.
- **Capa de Servicios (`bot/services/`)**:
  - `DatabaseService`: Gestiona operaciones con SQLite. Almacena y recupera datos de uso de los usuarios para la funcionalidad de límites del comando `/summarize` (tiempos de último uso, contadores diarios, etc.).
  - `OpenAIService`: Interactúa con OpenAI para resumen, transcripción y análisis de imágenes.
  - `DailySummaryService`, `SchedulerService`, `MessageService`: Mantienen sus roles actuales.
- **Capa de Utilidades (`bot/utils/`)**: Funciones auxiliares.
- **Configuración (`bot/config.py`)**: Gestión de configuraciones.
- **Punto de Entrada (`main.py`)**: Inicialización.

## 2. Decisiones Técnicas Clave

- **Framework del Bot**: `python-telegram-bot`.
- **Procesamiento de IA**: OpenAI (GPT-4o, GPT-4o-mini, Whisper).
- **Persistencia de Datos**: SQLite con `aiosqlite`. Se han añadido campos a `telegram_user` para gestionar los límites de uso del comando `/summarize`.
- **Programación Asíncrona**: `asyncio`, `async/await`.
- **Gestión de Límites de Uso**: La lógica de cooldowns y cuotas diarias para el comando `/summarize` está implementada directamente dentro del manejador del comando, interactuando con `DatabaseService`. Esto ha reemplazado la funcionalidad del decorador `@cooldown` para este comando.
- **Procesamiento Multimedia y de Contenido**: `ffmpeg`, `python-docx`, `PyPDF2`, `readability-lxml`, `youtube-transcript-api`.
- **Enfoque del Producto**: El bot se centrará exclusivamente en funcionalidades de resumen. Las capacidades de "asistente conversacional" se desarrollarán en un bot separado.

## 3. Patrones de Diseño en Uso

- **Singleton**: Para servicios.
- **Command**: El comando `/summarize` encapsula una lógica de negocio significativamente compleja, incluyendo la gestión de estado de uso del usuario.
- **Decorator**: El decorador `@cooldown` original ya no se aplica al comando `/summarize`. `@admin_command` se usa para otros comandos. `@log_command` y `@bot_started` se mantienen.
- **Strategy (Implícito)**: Dentro de `/summarize`, la elección del handler de contenido específico. Adicionalmente, la estrategia para aplicar límites varía según el tipo de usuario y operación.
- **Service Layer**: Mantenido.
- **Repository (Parcialmente con `DatabaseService`)**: `DatabaseService` abstrae el acceso a los datos de usuarios y sus límites de uso.

## 4. Relaciones entre Componentes

- `main.py` inicializa `Config`, `DatabaseService`, `TelegramBot`.
- `TelegramBot` registra `CommandHandler`s. El `summarize_command` es el más complejo.
- `summarize_command` utiliza `db_service` extensivamente para verificar y actualizar límites de uso antes de delegar a los handlers de contenido específico y a `openai_service`.
- Los handlers de contenido en `bot/handlers/` siguen utilizando `openai_service`.
- La separación del "Modo Compañero" significa que no habrá handlers dedicados a la conversación proactiva o menciones con respuesta conversacional en este bot.

## 5. Rutas Críticas de Implementación

- **Flujo del Comando `/summarize` (Implementado)**:
  1.  Recepción del comando.
  2.  `summarize_command` identifica usuario (`db_service`).
  3.  Si es admin, salta a procesamiento.
  4.  Si es gratuito:
      - Determina tipo de operación (simple/costosa) basado en si hay `reply_to_message` y el tipo de ese mensaje.
      - Consulta `db_service` por `last_usage_time` y `daily_count` para ese tipo de operación. (También verifica y resetea `daily_count` si la fecha de reseteo es pasada).
      - Verifica cooldown. Si falla, responde y termina.
      - Verifica límite diario (si es operación costosa). Si falla, responde y termina.
  5.  Procesa el resumen (delega a handler de contenido, luego a `openai_service`).
  6.  Envía respuesta.
  7.  Si es gratuito, actualiza `last_usage_time` y `daily_count` en `db_service`.
- **Flujo de Resumen Diario**: Sin cambios significativos.
- **Flujo de Guardado de Mensajes**: Sin cambios significativos.
