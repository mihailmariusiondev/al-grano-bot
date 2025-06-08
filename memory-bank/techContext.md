# Tech Context: Al-Grano Bot

## 1. Tecnologías Utilizadas

- **Lenguaje de Programación**: Python 3.12 (según `environment.yml`).
- **Framework del Bot de Telegram**: `python-telegram-bot`
- **Inteligencia Artificial (IA)**:
  - **Generación de Resúmenes (LLM)**:
    - **OpenRouter API**: Se utilizará para acceder a Modelos de Lenguaje Grandes (LLM).
    - Modelo LLM objetivo: `deepseek/deepseek-r1:free` (o un modelo similar de DeepSeek disponible y eficiente en OpenRouter).
    - Librería cliente: `openai` (configurada con `base_url="https://openrouter.ai/api/v1"` y `api_key` de OpenRouter).
  - **Transcripción de Audio**:
    - **API directa de OpenAI**: Se utilizará exclusivamente para el modelo Whisper-1.
    - Modelo de Transcripción: `whisper-1`.
    - Librería cliente: `openai` (configurada con `api_key` de OpenAI específica para Whisper).
  - _Nota: El análisis de imágenes con GPT-4o y el uso de GPT-4o/GPT-4o-mini para resúmenes directos vía API de OpenAI han sido eliminados/reemplazados._
- **Base de Datos**:
  - SQLite
  - Driver asíncrono: `aiosqlite`
  - Utilizada para almacenar usuarios (estado de admin, datos de uso para límites), mensajes, y estados de chat.
- **Programación de Tareas**: `APScheduler` (para resúmenes diarios).
- **Procesamiento Multimedia y de Archivos**:
  - `ffmpeg`: Para compresión de audio (a Opus) y extracción de audio de vídeos (a WAV PCM).
  - `youtube-transcript-api`: Para obtener transcripciones de vídeos de YouTube.
  - `readability-lxml`: Para extraer contenido principal de artículos web.
  - `python-docx`: Para leer archivos `.docx`.
  - `PyPDF2`: Para leer archivos `.pdf`.
  - `aiohttp`: Para descargas asíncronas de archivos (usado por `python-telegram-bot` internamente y potencialmente por `photo_handler` que será eliminado).
- **Manejo de Prompts**: Prompts del sistema externalizados en archivos Python dentro de un directorio `bot/prompts/`.
- **Manejo de Configuración**: `python-dotenv` (para cargar variables de entorno desde `.env`).
- **Logging**: Módulo `logging` estándar de Python, configurado a través de `bot/utils/logger.py`.
- **Serialización/Formato de Datos**: JSON, Markdown.
- **Gestión de Entorno y Dependencias**: Conda, `pip` (a través de `environment.yml`).
- **Tipado Estático**: Módulo `typing` de Python.
- **Utilidades de Fecha/Hora**: `datetime`, `pytz`.

## 2. Configuración de Desarrollo

- Se requiere un archivo `.env` en la raíz del proyecto con las siguientes variables:
  - `BOT_TOKEN`: Token del bot de Telegram.
  - `OPENROUTER_API_KEY`: Clave para la API de OpenRouter (para LLMs de resumen).
  - `OPENAI_API_KEY_FOR_WHISPER`: Clave de la API de OpenAI (exclusivamente para transcripciones con Whisper).
  - `DB_PATH` (opcional, por defecto `bot.db`).
  - `LOG_LEVEL` (opcional, por defecto `INFO`).
  - `AUTO_ADMIN_USER_IDS_CSV` (opcional, IDs de usuario de Telegram separados por comas para ser administradores automáticamente).
- Dependencias listadas en `environment.yml` deben estar instaladas.
- `ffmpeg` debe estar instalado y accesible en el PATH del sistema.
- El script principal para ejecutar el bot es `main.py`.

## 3. Restricciones Técnicas

- **Límites de la API de Telegram**:
  - Tamaño máximo de mensajes de texto (gestionado con `send_long_message`).
  - Límites de frecuencia de envío.
- **Límites de API (OpenRouter y OpenAI directa para Whisper)**:
  - Límites de tokens para los modelos (ej. `deepseek/deepseek-r1:free` tiene un contexto de ~160k tokens, pero los límites de salida pueden variar). Se revisará `MAX_INPUT_CHARS` en `OpenAIService` para alinearlo con el modelo DeepSeek y la estrategia de chunking.
  - Límites de frecuencia y cuotas de uso de las respectivas APIs.
- **Límites Implementados por el Bot (para Usuarios Gratuitos)**:
  - El comando `/summarize` tiene cooldowns y límites diarios para operaciones avanzadas/costosas.
- **Procesamiento de Archivos Grandes**:
  - `MAX_FILE_SIZE` (20MB) para archivos procesados localmente antes de enviarlos a APIs de transcripción.
  - La función `summarize_large_document` en `OpenAIService` dividirá el texto en chunks para evitar exceder los límites de tokens del LLM de OpenRouter.
- **Dependencia de `ffmpeg`**: Crítica para el procesamiento de audio y video.
- **Naturaleza Asíncrona**: Requerida para toda la E/S y operaciones de red.

## 4. Dependencias (Resumen de `environment.yml`)

- (Se asume que `environment.yml` se mantendrá actualizado con las librerías mencionadas, especialmente `openai`, `python-telegram-bot`, `aiosqlite`, etc.).

## 5. Patrones de Uso de Herramientas

- **`ffmpeg`**: Uso asíncrono para compresión y extracción de audio.
- **`OpenAIService` (Refactorizado)**:
  - Gestionará dos instancias de cliente `openai.AsyncOpenAI`:
    - Una configurada para OpenRouter (`base_url="https://openrouter.ai/api/v1"`, `api_key=config.OPENROUTER_API_KEY`) para llamadas a `chat.completions.create` usando modelos como `deepseek/deepseek-r1:free` para resúmenes.
    - Otra configurada para la API directa de OpenAI (`api_key=config.OPENAI_API_KEY_FOR_WHISPER`) para llamadas a `audio.transcriptions.create` con el modelo Whisper-1.
  - Los prompts del sistema se cargarán desde `bot/prompts/` (e.g., `summary_prompts.py`).
  - La estrategia "map-reduce" para `summarize_large_document` usará el modelo de DeepSeek (o similar vía OpenRouter) para el resumen final, y potencialmente un modelo más rápido/barato de OpenRouter para los chunks intermedios si se decide optimizar aún más.
  - La funcionalidad de análisis de imágenes ha sido eliminada.
- **`DatabaseService`**: Sin cambios mayores previstos en su interfaz, seguirá gestionando usuarios, mensajes, estados y límites de uso.
- **`Logger`**: Configuración estándar a través de `bot/utils/logger.py`.
- **`SchedulerService`**: Sin cambios mayores previstos.
- **`Config`**: Adaptada para cargar y proveer las nuevas claves de API (`OPENROUTER_API_KEY`, `OPENAI_API_KEY_FOR_WHISPER`) en lugar de una única `OPENAI_API_KEY`.
