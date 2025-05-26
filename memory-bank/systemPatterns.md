# System Patterns: Al-Grano Bot

## 1. Arquitectura del Sistema

El "Al-Grano Bot" sigue una arquitectura modular enfocada en la funcionalidad de resumen:

- **Capa de Interfaz (Telegram)**: `TelegramBot` (`bot/bot.py`) gestiona la comunicación con la API de Telegram.
- **Capa de Comandos (`bot/commands/`)**: Contiene manejadores para comandos. El comando `/summarize` es central y contiene lógica compleja para:
  - Identificación del tipo de usuario (admin/gratuito).
  - Clasificación del tipo de operación de resumen (simple/costosa).
  - Aplicación de límites de uso (cooldowns, cuotas diarias) para usuarios gratuitos.
  - Delegación a handlers de contenido específico.
  - (El comando `/about` ha sido diferido y no se implementará).
- **Capa de Manejadores de Contenido (`bot/handlers/`)**: Módulos para procesar tipos específicos de contenido para resumen (audio, video, documento, artículo web, YouTube). Son invocados por el comando `/summarize`. El `message_handler.py` genérico (en `bot/commands/`) guarda mensajes para el contexto de resúmenes de chat. (El `photo_handler.py` será eliminado, y el manejo de encuestas directamente en `summarize_command.py` también será removido).
- **Capa de Servicios (`bot/services/`)**:
  - `DatabaseService`: Gestiona operaciones con SQLite. Almacena y recupera datos de uso de los usuarios para la funcionalidad de límites del comando `/summarize`.
  - `OpenAIService`:
    - Utilizará un cliente `openai.AsyncOpenAI` configurado para **OpenRouter API** (ej. con `deepseek/deepseek-r1:free`) para todas las tareas de generación de resúmenes.
    - Utilizará otro cliente `openai.AsyncOpenAI` configurado para la **API directa de OpenAI** exclusivamente para transcripciones con el modelo Whisper-1.
  - `DailySummaryService`, `SchedulerService`, `MessageService`: Mantienen sus roles actuales, pero `DailySummaryService` usará el `OpenAIService` refactorizado.
- **Capa de Utilidades (`bot/utils/`)**: Funciones auxiliares.
- **Capa de Prompts (`bot/prompts/`)**: (Nueva) Directorio que contendrá los prompts del sistema para los modelos de IA, externalizados desde `OpenAIService`. Se importarán desde un módulo como `bot.prompts.summary_prompts`.
- **Configuración (`bot/config.py`)**: Gestión de configuraciones, incluyendo las nuevas API keys.
- **Punto de Entrada (`main.py`)**: Inicialización.

## 2. Decisiones Técnicas Clave

- **Framework del Bot**: `python-telegram-bot`.
- **Procesamiento de IA (Refactorizado)**:
  - **OpenRouter API**: Para LLMs (ej. `deepseek/deepseek-r1:free` o similar) encargados de todas las tareas de generación de resúmenes.
  - **API directa de OpenAI**: Exclusivamente para transcripción de audio con Whisper-1.
- **Persistencia de Datos**: SQLite con `aiosqlite`.
- **Programación Asíncrona**: `asyncio`, `async/await`.
- **Gestión de Límites de Uso**: Lógica de cooldowns y cuotas diarias en `summarize_command.py`.
- **Procesamiento Multimedia y de Contenido**: `ffmpeg`, `python-docx`, `PyPDF2`, `readability-lxml`, `youtube-transcript-api`.
- **Enfoque del Producto**: Foco exclusivo en resúmenes de texto y multimedia principal (audio, video, documentos, enlaces). Funcionalidades de resumen de fotos/imágenes y encuestas han sido eliminadas. El comando `/about` ha sido diferido.
- **Externalización de Prompts**: Los prompts del sistema se moverán a un directorio dedicado (`bot/prompts/`) y se gestionarán en un módulo Python (e.g., `summary_prompts.py`).

## 3. Patrones de Diseño en Uso

- **Singleton**: Para servicios (`DatabaseService`, `OpenAIService`, `SchedulerService`, `MessageService`, `Logger`, `Config`, `TelegramBot`).
- **Command**: El comando `/summarize` encapsula lógica de negocio compleja.
- **Decorator**: `@admin_command`, `@log_command`, `@bot_started`.
- **Strategy (Implícito)**: Dentro de `/summarize`, la elección del handler de contenido y la lógica de IA a aplicar.
- **Service Layer**: Mantenido y reforzado con la refactorización de `OpenAIService`.
- **Repository (Parcialmente con `DatabaseService`)**: `DatabaseService` abstrae el acceso a datos.

## 4. Relaciones entre Componentes

- `main.py` inicializa `Config`, `DatabaseService`, `TelegramBot`.
- `TelegramBot` registra `CommandHandler`s.
- `summarize_command` utiliza `db_service` y delegará a `openai_service`.
- Los handlers de contenido en `bot/handlers/` utilizan `openai_service` para transcripción y/o pasan contenido a `summarize_command` que luego usa `openai_service` para resumen. (El `photo_handler.py` será eliminado).
- `OpenAIService` obtendrá prompts desde `bot/prompts/summary_prompts.py` (o similar).
- `OpenAIService` gestionará dos instancias de cliente `AsyncOpenAI`: una para OpenRouter y otra para OpenAI directa (Whisper).
- `Config` proveerá las API keys necesarias (`OPENROUTER_API_KEY`, `OPENAI_API_KEY_FOR_WHISPER`).

## 5. Rutas Críticas de Implementación

- **Flujo del Comando `/summarize` (Modificado)**:
  1.  Recepción del comando.
  2.  `summarize_command` identifica usuario y tipo de operación.
  3.  Gestión de límites para usuarios gratuitos.
  4.  Identificación del tipo de mensaje/contenido (texto, enlace, audio, video, documento).
      - El manejo de fotos y encuestas será eliminado.
  5.  Procesamiento del contenido:
      - Para audio/video:
        - Si es necesario, se usa `ffmpeg` para procesar.
        - Se llama a `openai_service.transcribe_audio()` (usando API directa de OpenAI con Whisper).
      - Para documentos/artículos/YouTube: Se extrae el texto.
  6.  Generación del resumen:
      - Se llama a `openai_service.get_summary()` o `openai_service.summarize_large_document()` (usando OpenRouter con DeepSeek o similar, y prompts externalizados).
  7.  Envío de respuesta.
  8.  Actualización de contadores de uso en `db_service`.
- **Flujo de Resumen Diario**: Utilizará el `OpenAIService` refactorizado con OpenRouter/DeepSeek y prompts externalizados.
- **Flujo de Guardado de Mensajes**: Sin cambios significativos, pero `get_message_type` no incluirá `photo` ni `poll`.
