# Al-Grano Bot: Tu Asistente Inteligente de Resúmenes en Telegram

**Al-Grano Bot** es un bot de Telegram avanzado diseñado para ayudarte a procesar y entender grandes cantidades de información de manera rápida y eficiente. Ya sea para ponerte al día con conversaciones de chat extensas, resumir vídeos de YouTube, extraer la esencia de artículos web o analizar documentos, Al-Grano Bot te ofrece la información clave "al grano".

## 🌟 Características Principales

- **Resúmenes de Chat Inteligentes**:
  - Genera resúmenes de los últimos mensajes en un chat grupal (hasta 300 mensajes).
  - Permite a los administradores elegir entre resúmenes **largos y detallados** o **cortos y concisos** para el chat.
- **Resúmenes de Contenido Específico (usando `/summarize` en respuesta a un mensaje)**:
  - **Mensajes de texto**: Resume el texto del mensaje citado.
  - **Vídeos de YouTube**: Extrae la transcripción (si está disponible) y la resume.
  - **Artículos web**: Extrae el contenido principal del artículo y lo resume.
  - **Mensajes de voz y archivos de audio**: Transcribe el audio y luego resume la transcripción.
  - **Vídeos y notas de vídeo de Telegram**: Extrae el audio, lo transcribe y resume la transcripción.
  - **Documentos (PDF, DOCX, TXT)**: Extrae el texto del documento y lo resume. Capaz de manejar documentos grandes mediante división en fragmentos.
- **Resúmenes Diarios Automatizados**:
  - Opción para administradores de activar/desactivar un resumen diario automático de la actividad del chat (enviado a las 3 AM hora de Madrid).
- **Gestión de Uso y Límites (para usuarios no administradores)**:
  - **Operaciones Simples** (resumir chat, texto, enlaces a YouTube/artículos con transcripción/extracción directa): Cooldown entre usos.
  - **Operaciones Avanzadas** (transcribir audio/video, procesar documentos): Cooldown más largo y límite diario de operaciones.
  - Los administradores no tienen estas limitaciones.
- **Procesamiento Multimedia y de Contenido**:
  - Utiliza `ffmpeg` para la compresión de audio (a Opus) y extracción de audio de vídeos (a WAV PCM).
  - Integración con **OpenRouter API** (usando modelos como `deepseek/deepseek-r1:free`) para la generación de todos los resúmenes.
  - Integración con la **API directa de OpenAI** (modelo `whisper-1`) exclusivamente para la transcripción de audio.
  - Prompts del sistema para la IA externalizados y gestionados de forma modular.
- **Interfaz Amigable**:
  - Comandos intuitivos (`/start`, `/help`, `/summarize`).
  - Mensajes de progreso durante operaciones largas.
  - Mensajes de ayuda detallados accesibles con `/help`.
  - Exporta los mensajes del día en un archivo JSON con `/export_chat`.
- **Administración del Bot**:
  - Interfaz de configuración `/configurar_resumen` con permisos administrativos para cambiar configuraciones del chat.
  - Los administradores pueden ser definidos automáticamente a través de una variable de entorno.
- **Persistencia de Datos**:
  - Almacena mensajes (para resúmenes de chat), estados de chat y datos de usuario (para gestión de límites) en una base de datos SQLite.
  - Limpieza automática de mensajes antiguos para mantener un histórico relevante.
- **Logging y Manejo de Errores**:
  - Sistema de logging detallado.
  - Manejador de errores global que notifica a los administradores en caso de problemas críticos.

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.12
- **Framework del Bot**: `python-telegram-bot`
- **IA y NLP**:
  - **OpenRouter API**: Para generación de resúmenes (e.g., usando modelos `deepseek/deepseek-r1:free`).
  - **OpenAI API (directa)**: Exclusivamente para transcripción de audio con `whisper-1`.
- **Base de Datos**: SQLite (con `aiosqlite` para operaciones asíncronas)
- **Procesamiento Multimedia**: `ffmpeg`
- **Extracción de Contenido**:
  - `youtube-transcript-api` (para transcripciones de YouTube)
  - `readability-lxml` (para contenido de artículos web)
  - `python-docx` (para archivos `.docx`)
  - `PyPDF2` (para archivos `.pdf`)
- **Programación de Tareas**: `APScheduler` (para resúmenes diarios)
- **Gestión de Entorno**: Conda y Pip
- **Otros**: `python-dotenv` (variables de entorno), `pytz` (zonas horarias), `asyncio`.

## 📋 Requisitos Previos

- Python 3.12 o superior.
- Conda (recomendado para gestionar el entorno).
- `ffmpeg` instalado y accesible en el PATH del sistema.
- Una cuenta de Telegram y un token de bot.
- Una clave de API para OpenRouter.
- Una clave de API para OpenAI (específicamente para el uso del modelo Whisper).

## 🚀 Configuración e Instalación

1.  **Clonar el Repositorio**:

    ```bash
    git clone https://github.com/mihailmariusiondev/al-grano-bot.git
    cd al-grano-bot
    ```

2.  **Crear y Activar el Entorno Conda**:

    ```bash
    conda env create -f environment.yml
    conda activate al-grano-bot
    ```

3.  **Configurar Variables de Entorno**:
    Crea un archivo `.env` en la raíz del proyecto y añade tus credenciales:

    ```env
    BOT_TOKEN="TU_TOKEN_DE_TELEGRAM"
    OPENROUTER_API_KEY="TU_CLAVE_DE_API_DE_OPENROUTER"
    OPENAI_API_KEY="TU_CLAVE_DE_API_DE_OPENAI_PARA_WHISPER" # Usada para transcripciones con Whisper

    # Opcionales para OpenRouter (valores por defecto o ejemplos mostrados)
    # OPENROUTER_SITE_URL="https://github.com/mihailmariusiondev/al-grano-bot"
    # OPENROUTER_SITE_NAME="Al-Grano Bot"
    # OPENROUTER_PRIMARY_MODEL="deepseek/deepseek-r1:free"
    # OPENROUTER_FALLBACK_MODEL="deepseek/deepseek-r1"

    # Opcionales (valores por defecto mostrados)
    # DB_PATH="bot.db"
    # LOG_LEVEL="INFO"
    # AUTO_ADMIN_USER_IDS_CSV="ID_USUARIO_1,ID_USUARIO_2" # IDs de Telegram separados por comas
    ```

    _Nota: `OPENAI_API_KEY` se utiliza específicamente para las llamadas al servicio de transcripción Whisper de OpenAI. Todos los resúmenes se generan a través de OpenRouter._

4.  **(Opcional) Asignar Administradores Automáticos**:
    Puedes configurar la variable `AUTO_ADMIN_USER_IDS_CSV` en tu archivo `.env` con una lista de IDs de usuario de Telegram separados por comas. Estos usuarios serán configurados como administradores automáticamente al iniciar el bot. Alternativamente, puedes asignar administradores manualmente en la base de datos (`telegram_user` tabla, campo `is_admin = 1`) después de que el bot haya interactuado con ellos.

## ▶️ Uso

1.  **Iniciar el Bot**:

    ```bash
    python main.py
    ```

2.  **Comandos Disponibles en Telegram** (extraído y adaptado del comando `/help` del bot):

    - `/start`: Inicia el bot en el chat. Registra el chat y el usuario.
    - `/help`: Muestra una guía de ayuda detallada con todos los comandos y funcionalidades.
    - `/summarize`:
      - **Sin responder a un mensaje (Operación Simple)**: Genera un resumen de los últimos mensajes del chat (hasta 300). _Cooldown: 2 minutos para usuarios no admins._
      - **Respondiendo a un mensaje (Operación Simple o Avanzada)**:
        - **Texto simple, enlaces a YouTube, artículos web**: _Cooldown: 2 minutos para usuarios no admins._
        - **Archivos de Audio/Voz, Vídeos/Notas de Vídeo, Documentos (PDF, DOCX, TXT)**: Considerado "Operación Avanzada". _Cooldown: 10 minutos y límite de 5 operaciones/día para usuarios no admins._
    - `/configurar_resumen`: Personaliza la configuración de resúmenes (tono, longitud, idioma, inclusión de nombres, resúmenes diarios automáticos). Los administradores pueden cambiar la configuración del chat.
    - `/export_chat`: Envía un archivo `.json` con los mensajes del día en curso.

    **Nota sobre límites (para usuarios no administradores):**

    - Operaciones simples (resumir chat, texto, enlaces): Tienen un cooldown corto.
    - Operaciones avanzadas (transcribir audio/video, procesar documentos): Tienen un cooldown más largo y un límite diario de usos.
    - Los administradores no están sujetos a estos cooldowns o límites.
    - Tamaño máximo de archivo para procesamiento: 20MB.

## 📂 Estructura del Proyecto (Simplificada)

```
al-grano-bot/
├── bot/
│   ├── commands/         # Lógica para los comandos del bot (/start, /summarize, etc.)
│   ├── handlers/         # Manejadores para tipos de contenido (audio, video, docs, etc.)
│   ├── prompts/          # Prompts del sistema para la IA
│   ├── services/         # Servicios de negocio (IA, base de datos, scheduler)
│   ├── utils/            # Utilidades (logger, decoradores, formateo, constantes)
│   ├── __init__.py
│   ├── bot.py            # Lógica principal del bot, registro de handlers
│   └── config.py         # Carga de configuración
├── logs/                 # Archivos de log (creados en ejecución)
├── .env                  # Archivo de variables de entorno (debes crearlo)
├── environment.yml       # Definición del entorno Conda
├── main.py              # Punto de entrada de la aplicación
└── README.md            # Este archivo
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un _issue_ para discutir cambios importantes o envía un _pull request_.

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👨‍💻 Autor

Este bot ha sido creado por **Mihail Marius Ion ([@Arkantos2374](https://t.me/Arkantos2374))**.

Si deseas apoyar el desarrollo y mantenimiento del bot, puedes considerar una donación vía [PayPal](https://paypal.me/mariusmihailion).
