# System Patterns: Al-Grano Bot

## 1. Arquitectura del Sistema

El "Al-Grano Bot" sigue una arquitectura modular común en aplicaciones de bots, especialmente aquellos construidos con la librería `python-telegram-bot`. La estructura general se puede describir como:

- **Capa de Interfaz (Telegram)**: Gestionada por la clase `TelegramBot` (`bot/bot.py`), que utiliza `python-telegram-bot` para recibir actualizaciones (mensajes, comandos) de la API de Telegram y enviar respuestas.
- **Capa de Comandos (`bot/commands/`)**: Contiene manejadores específicos para cada comando del bot (ej. `/start`, `/summarize`, `/help`). Estos módulos definen la lógica principal de cada comando.
- **Capa de Manejadores (`bot/handlers/`)**:
  - Manejadores de tipos de contenido específico (ej. `audio_handler.py`, `video_handler.py`, `document_handler.py`, `photo_handler.py`, `article_handler.py`, `youtube_handler.py`). Estos son invocados principalmente por el comando `/summarize` cuando se responde a un mensaje con contenido.
  - Manejador de mensajes genérico (`message_handler.py` en `bot/commands/`): Guarda todos los mensajes de texto en la base de datos para su posterior resumen.
  - Manejador de errores (`error_handler.py`): Centraliza la gestión de excepciones.
- **Capa de Servicios (`bot/services/`)**: Abstrae la lógica de negocio y las interacciones con sistemas externos.
  - `DatabaseService`: Gestiona todas las operaciones con la base de datos SQLite.
  - `OpenAIService`: Interactúa con la API de OpenAI para tareas de IA (resumen, transcripción, análisis de imágenes).
  - `DailySummaryService`: Contiene la lógica para generar y enviar resúmenes diarios.
  - `SchedulerService`: Gestiona tareas programadas (actualmente, el resumen diario) usando `APScheduler`.
  - `MessageService`: Un servicio para enviar mensajes a través del bot, útil para componentes desacoplados como el `SchedulerService`.
- **Capa de Utilidades (`bot/utils/`)**: Proporciona funciones y constantes auxiliares reutilizables en todo el proyecto (formateo, logging, decoradores, constantes, procesamiento de medios, etc.).
- **Configuración (`bot/config.py`)**: Gestiona la carga de configuraciones desde variables de entorno.
- **Punto de Entrada (`main.py`)**: Inicializa la configuración, la base de datos, el bot y lo pone en marcha.

## 2. Decisiones Técnicas Clave

- **Framework del Bot**: `python-telegram-bot` es la librería principal para la interacción con la API de Telegram.
- **Procesamiento de IA**: OpenAI (GPT-4o, GPT-4o-mini, Whisper) es la elección para la generación de resúmenes, transcripción de audio y análisis de imágenes.
- **Persistencia de Datos**: SQLite es la base de datos elegida, accedida de forma asíncrona mediante `aiosqlite`.
- **Programación Asíncrona**: Uso extenso de `asyncio` y `async/await` para operaciones no bloqueantes, esencial para un bot responsivo.
- **Programación de Tareas**: `APScheduler` se utiliza para tareas en segundo plano, como los resúmenes diarios.
- **Procesamiento Multimedia**: `ffmpeg` se utiliza para la compresión de audio y extracción de audio de vídeos. Librerías específicas como `python-docx`, `PyPDF2`, `readability-lxml`, `youtube-transcript-api` se usan para manejar diferentes formatos de archivo y contenido web.
- **Configuración Segura**: Las claves de API y otras configuraciones sensibles se gestionan a través de variables de entorno.
- **Logging Centralizado**: Un servicio de logging personalizado (`Logger` en `bot/utils/logger.py`) para un seguimiento consistente.

## 3. Patrones de Diseño en Uso

- **Singleton**: Varios servicios (`DatabaseService`, `OpenAIService`, `TelegramBot`, `Config`, `Logger`, `MessageService`, `SchedulerService`) se implementan utilizando el patrón Singleton. Esto asegura que solo exista una instancia de estos servicios en toda la aplicación.
- **Command**: La estructura de `python-telegram-bot` con `CommandHandler` y `MessageHandler` sigue inherentemente el patrón Command, donde cada comando o tipo de mensaje se encapsula como un objeto (el handler) que conoce cómo ejecutar la acción asociada.
- **Decorator**: Utilizado بكثرة (`@log_command`, `@admin_command`, `@premium_only`, `@bot_started`, `@cooldown`) para añadir funcionalidades transversales a las funciones de comando de manera declarativa y no intrusiva.
- **Strategy (Implícito)**:
  - En `summarize_command.py`, la lógica para manejar diferentes tipos de mensajes (`message_type` con `match/case`) puede verse como una forma de Strategy, donde se elige un algoritmo (handler específico) diferente según el tipo de mensaje.
  - En `OpenAIService`, los `SUMMARY_PROMPTS` actúan como estrategias diferentes para generar resúmenes según el `summary_type`.
- **Service Layer**: La carpeta `services` indica una separación de la lógica de negocio en componentes cohesivos.
- **Repository (Parcialmente con `DatabaseService`)**: `DatabaseService` actúa como una capa de abstracción sobre la base de datos, centralizando el acceso a los datos, similar al patrón Repository.
- **Chain of Responsibility (Implícito en el manejo de errores de `python-telegram-bot`)**: Aunque no explícitamente definido por el usuario, la forma en que los handlers y el error_handler son registrados en la aplicación de `python-telegram-bot` puede tener características de este patrón.

## 4. Relaciones entre Componentes

- `main.py` inicializa `Config`, `DatabaseService`, `TelegramBot`.
- `TelegramBot` registra `CommandHandler`s (de `bot/commands/`) y `MessageHandler`s (de `bot/handlers/` o `bot/commands/`). También inicializa `MessageService` y `SchedulerService`.
- Los comandos en `bot/commands/` utilizan servicios de `bot/services/` (ej. `db_service`, `openai_service`) y pueden delegar a manejadores específicos de `bot/handlers/`.
- Los manejadores en `bot/handlers/` utilizan servicios (principalmente `openai_service` para procesamiento de contenido) y utilidades de `bot/utils/`.
- `DailySummaryService` utiliza `db_service` para obtener datos, `openai_service` para generar resúmenes, y `message_service` para enviar los resúmenes.
- `SchedulerService` invoca a `DailySummaryService`.
- Casi todos los módulos utilizan `Logger` de `bot/utils/logger.py`.
- `DatabaseService` es fundamental, ya que muchos componentes leen o escriben estados y datos.

## 5. Rutas Críticas de Implementación

- **Flujo de Comando `/summarize`**:
  1.  `TelegramBot` recibe el comando.
  2.  Se invoca `summarize_command.py`.
  3.  Determina si es un resumen de chat o de mensaje específico.
  4.  Si es de mensaje específico, `get_message_type` determina el tipo.
  5.  Se invoca el handler adecuado (`youtube_handler`, `video_handler`, `document_handler`, etc.).
  6.  El handler procesa el contenido (descarga, extracción de texto/audio).
  7.  Se invoca `OpenAIService` para transcripción (si es audio/video) o análisis de imagen.
  8.  Se invoca `OpenAIService` para generar el resumen con el prompt adecuado.
  9.  El resultado se envía al usuario.
- **Flujo de Resumen Diario**:
  1.  `SchedulerService` activa `send_daily_summaries` en `DailySummaryService` a la hora programada.
  2.  `DailySummaryService` obtiene los chats con resúmenes diarios activados de `DatabaseService`.
  3.  Para cada chat, obtiene los mensajes del día anterior de `DatabaseService`.
  4.  Formatea los mensajes y obtiene el tipo de resumen preferido del chat desde `DatabaseService`.
  5.  Invoca `OpenAIService` para generar el resumen.
  6.  Utiliza `MessageService` para enviar el resumen al chat.
- **Flujo de Guardado de Mensajes**:
  1.  `TelegramBot` recibe un mensaje.
  2.  Se invoca `message_handler.py` (en `bot/commands/`).
  3.  Se obtienen/crean el usuario y el estado del chat a través de `DatabaseService`.
  4.  El mensaje se guarda en la base de datos mediante `DatabaseService`.
