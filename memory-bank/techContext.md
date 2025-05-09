# Tech Context: Al-Grano Bot

## 1. Tecnologías Utilizadas

- **Lenguaje de Programación**: Python 3.12 (según `environment.yml`).
- **Framework del Bot de Telegram**: `python-telegram-bot`
- **Inteligencia Artificial**:
  - API de OpenAI:
    - Modelos de Lenguaje (LLM): GPT-4o, GPT-4o-mini (para resúmenes, análisis de documentos).
    - Modelo de Transcripción: Whisper-1 (para audio y vídeo).
    - Análisis de Imágenes: GPT-4o (con capacidad de visión).
  - Librería cliente: `openai`
- **Base de Datos**:
  - SQLite
  - Driver asíncrono: `aiosqlite`
- **Programación de Tareas**: `APScheduler` (para resúmenes diarios).
- **Procesamiento Multimedia y de Archivos**:
  - `ffmpeg`: Para compresión de audio (a Opus) y extracción de audio de vídeos (a WAV PCM). Se invoca como un proceso de línea de comandos.
  - `youtube-transcript-api`: Para obtener transcripciones de vídeos de YouTube.
  - `readability-lxml` (implícito por `readability.parse`): Para extraer contenido principal de artículos web.
  - `python-docx`: Para leer archivos `.docx`.
  - `PyPDF2`: Para leer archivos `.pdf`.
  - `aiohttp`: Para descargas asíncronas de archivos (ej. imágenes para análisis).
- **Manejo de Configuración**: `python-dotenv` (para cargar variables de entorno desde `.env`).
- **Logging**: Módulo `logging` estándar de Python, con configuración personalizada y `RotatingFileHandler`.
- **Serialización/Formato de Datos**: JSON (implícito en interacciones con APIs), Markdown (para formatear mensajes de respuesta).
- **Gestión de Entorno y Dependencias**: Conda (según `environment.yml`), con `pip` para algunas dependencias.
- **Tipado Estático**: Módulo `typing` de Python.
- **Utilidades de Fecha/Hora**: `datetime`, `pytz` (para manejo de zonas horarias, específicamente "Europe/Madrid").

## 2. Configuración de Desarrollo (Inferida)

- Se requiere un archivo `.env` en la raíz del proyecto con las siguientes variables:
  - `BOT_TOKEN`: Token del bot de Telegram.
  - `OPENAI_API_KEY`: Clave de la API de OpenAI.
  - `DB_PATH` (opcional, por defecto `bot.db`): Ruta al archivo de la base de datos SQLite.
  - `DEBUG_MODE` (opcional, por defecto `false`): Si es `true`, establece el nivel de log a DEBUG.
  - `LOG_LEVEL` (opcional, por defecto `INFO`): Nivel de logging (ej. `INFO`, `DEBUG`, `WARNING`).
  - `ENVIRONMENT` (opcional, por defecto `development`): Entorno de ejecución.
- Dependencias listadas en `environment.yml` deben estar instaladas.
- `ffmpeg` debe estar instalado y accesible en el PATH del sistema para que funcionen las utilidades de `media_utils.py`.
- El script principal para ejecutar el bot es `main.py`.

## 3. Restricciones Técnicas

- **Límites de la API de Telegram**:
  - Tamaño máximo de mensajes de texto (gestionado con `send_long_message`).
  - Límites de frecuencia de envío (rate limits), aunque no hay un manejo explícito más allá del cooldown por comando.
- **Límites de la API de OpenAI**:
  - Límites de tokens para los modelos (ej. GPT-4o tiene un límite de 128k tokens). `OpenAIService` tiene una constante `MAX_INPUT_CHARS` para tratar de manejar esto, y `summarize_large_document` divide el texto si es necesario.
  - Límites de frecuencia y cuotas de uso de la API.
- **Procesamiento de Archivos Grandes**:
  - `MAX_FILE_SIZE` (20MB) se define en `constants.py` para limitar el tamaño de archivos de audio/vídeo procesados localmente antes de enviarlos a OpenAI.
  - El procesamiento de documentos grandes (`summarize_large_document`) divide el texto en chunks para evitar exceder los límites de tokens de OpenAI, usando GPT-4o-mini para chunks intermedios y GPT-4o para el resumen final.
- **Dependencia de `ffmpeg`**: Las funcionalidades de compresión de audio y extracción de audio de vídeo dependen de que `ffmpeg` esté correctamente instalado en el entorno de ejecución.
- **Naturaleza Asíncrona**: Toda la lógica de E/S debe ser asíncrona para no bloquear el bucle de eventos del bot.

## 4. Dependencias (Resumen de `environment.yml`)

- `python=3.12`
- `pip`
- `python-telegram-bot`: Interfaz con la API de Telegram.
- `python-dotenv`: Carga de variables de entorno.
- `openai`: Cliente para la API de OpenAI.
- `aiosqlite`: Acceso asíncrono a SQLite.
- `youtube-transcript-api`: Obtención de transcripciones de YouTube.
- `python-readability` (probablemente `readability-lxml`): Extracción de contenido de artículos web.
- `python-docx`: Lectura de archivos DOCX.
- `PyPDF2`: Lectura de archivos PDF.
- `pytz`: Manejo de zonas horarias.
- `APScheduler`: Programación de tareas.
- (Implícitas o transitivas no listadas directamente pero usadas: `aiohttp` para descargas asíncronas de imágenes).

## 5. Patrones de Uso de Herramientas

- **`ffmpeg`**: Se utiliza mediante `asyncio.create_subprocess_exec` para ejecutar comandos de `ffmpeg` de forma asíncrona para:
  - Comprimir audio al formato Opus (`libopus`) con una tasa de bits baja (12k) y aplicación VoIP, optimizado para voz.
  - Extraer audio de vídeos a formato WAV (pcm_s16le, mono, 16000 Hz), un formato común para APIs de transcripción.
- **`OpenAIService`**:
  - Utiliza `client.chat.completions.create` para interactuar con los modelos de lenguaje.
  - Utiliza `client.audio.transcriptions.create` para el modelo Whisper.
  - Maneja la lógica de prompts dinámicos según el tipo de resumen y el idioma.
  - Implementa una estrategia de "map-reduce" para documentos grandes (`summarize_large_document`), resumiendo chunks y luego resumiendo los resúmenes.
- **`DatabaseService`**:
  - Usa `aiosqlite` para todas las interacciones con la BD.
  - Define el esquema de la BD, incluyendo triggers para `updated_at` y limpieza de mensajes antiguos.
  - Proporciona métodos CRUD asíncronos y consultas específicas.
- **`Logger`**: Configura un logger raíz y permite obtener loggers específicos por módulo, con handlers para consola y archivos rotatorios. El nivel de log y el formato son configurables.
- **`SchedulerService`**: Configura `AsyncIOScheduler` de `APScheduler` con un `CronTrigger` para ejecutar `send_daily_summaries` a una hora fija en la zona horaria "Europe/Madrid".
