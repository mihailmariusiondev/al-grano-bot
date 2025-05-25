# Al-Grano Bot: Tu Asistente Inteligente de Resúmenes en Telegram

**Al-Grano Bot** es un bot de Telegram avanzado diseñado para ayudarte a procesar y entender grandes cantidades de información de manera rápida y eficiente. Ya sea para ponerte al día con conversaciones de chat extensas, resumir vídeos de YouTube, extraer la esencia de artículos web o analizar documentos, Al-Grano Bot te ofrece la información clave "al grano".

## 🌟 Características Principales

- **Resúmenes de Chat Inteligentes**:
  - Genera resúmenes de los últimos mensajes en un chat grupal.
  - Permite elegir entre resúmenes **largos y detallados** o **cortos y concisos**.
- **Resúmenes de Contenido Específico**:
  - Responde a un mensaje con `/summarize` para obtener un resumen de:
    - Mensajes de texto.
    - Vídeos de YouTube (a partir de sus transcripciones).
    - Artículos web.
    - Mensajes de voz y archivos de audio (transcripción y resumen).
    - Vídeos y notas de vídeo de Telegram (extracción de audio, transcripción y resumen).
    - Documentos (PDF, DOCX, TXT).
    - Imágenes (análisis y descripción detallada).
    - Encuestas.
- **Resúmenes Diarios Automatizados**:
  - Opción de recibir un resumen diario automático de la actividad del chat a una hora programada (configurable por administradores).
- **Procesamiento Multimedia Avanzado**:
  - Utiliza `ffmpeg` para el procesamiento de audio y vídeo.
  - Integración con la API de OpenAI (GPT-4o, Whisper) para transcripciones, análisis de imágenes y generación de resúmenes de alta calidad.
- **Interfaz Amigable**:
  - Comandos intuitivos y mensajes de progreso para una mejor experiencia de usuario.
  - Mensajes de ayuda detallados.
- **Gestión de Usuarios**:
- **Persistencia de Datos**:
  - Almacena mensajes y configuraciones en una base de datos SQLite para un funcionamiento eficiente.

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.12
- **Framework del Bot**: `python-telegram-bot`
- **IA y NLP**: API de OpenAI (GPT-4o, GPT-4o-mini, Whisper)
- **Base de Datos**: SQLite (con `aiosqlite` para operaciones asíncronas)
- **Procesamiento Multimedia**: `ffmpeg`
- **Manejo de Archivos**: `python-docx`, `PyPDF2`, `readability-lxml`
- **Programación de Tareas**: `APScheduler`
- **Gestión de Entorno**: Conda y Pip
- **Otros**: `python-dotenv`, `pytz`, `aiohttp`

## 📋 Requisitos Previos

- Python 3.12 o superior.
- Conda (recomendado para gestionar el entorno).
- `ffmpeg` instalado y accesible en el PATH del sistema.
- Una cuenta de Telegram y un token de bot.
- Una clave de API de OpenAI.

## 🚀 Configuración e Instalación

1.  **Clonar el Repositorio**:

    ```bash
    git clone https://github.com/tu-usuario/al-grano-bot.git
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
    OPENAI_API_KEY="TU_CLAVE_DE_API_DE_OPENAI"

    # Opcionales (valores por defecto mostrados)
    # DB_PATH="bot.db"
    # DEBUG_MODE="false"
    # LOG_LEVEL="INFO"
    # ENVIRONMENT="development"
    ```

4.  **(Opcional) Asignar Administradores**:
    Puedes asignar administradores manualmente en la base de datos (`telegram_user` tabla, campo `is_admin = 1`) después de que el bot haya interactuado con ellos por primera vez y se hayan registrado en la base de datos.

## ▶️ Uso

1.  **Iniciar el Bot**:

    ```bash
    python main.py
    ```

2.  **Comandos Disponibles en Telegram**:

    - `/start`: Inicia el bot y muestra un mensaje de bienvenida. Registra el chat y el usuario.
    - `/help`: Muestra una guía de ayuda detallada con todos los comandos y funcionalidades.
    - `/summarize`:
      - **Sin responder a un mensaje**: Genera un resumen de los últimos 300 mensajes del chat.
      - **Respondiendo a un mensaje**: Genera un resumen del contenido específico de ese mensaje (texto, enlace de YouTube, documento, audio, vídeo, imagen, encuesta, etc.).
    - `/toggle_daily_summary` (Solo Admins): Activa o desactiva el resumen diario automático del chat (se envía a las 3 AM hora de Madrid).
    - `/toggle_summary_type` (Solo Admins): Alterna entre resúmenes largos (detallados) y cortos (concisos) para los resúmenes de chat y diarios.
    - `/about` (Próximamente): Proporciona información sobre el creador y el propósito del bot.

    _(Basado en el contenido del comando `/help` interno del bot)_

## 📂 Estructura del Proyecto (Simplificada)

```
al-grano-bot/
├── bot/
│   ├── commands/         # Lógica para los comandos del bot (/start, /summarize, etc.)
│   ├── handlers/         # Manejadores para tipos de contenido (audio, video, docs, etc.)
│   ├── services/         # Servicios de negocio (OpenAI, base de datos, scheduler)
│   ├── utils/            # Utilidades (logger, decoradores, formateo, constantes)
│   ├── __init__.py
│   ├── bot.py            # Lógica principal del bot, registro de handlers
│   └── config.py         # Carga de configuración
├── logs/                 # Archivos de log (creados en ejecución)
├── .env                  # Archivo de variables de entorno (debes crearlo)
├── environment.yml       # Definición del entorno Conda
├── main.py               # Punto de entrada de la aplicación
└── README.md             # Este archivo
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un _issue_ para discutir cambios importantes o envía un _pull request_.

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles (si existiera, si no, puedes añadir una).

## 👨‍💻 Autor

Este bot ha sido creado por **[@Arkantos2374](https://t.me/Arkantos2374)**.

Si deseas apoyar el desarrollo y mantenimiento del bot, puedes considerar una donación vía [PayPal](https://paypal.me/mariusmihailion).
