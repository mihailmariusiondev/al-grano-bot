# Al-Grano Bot: Tu Asistente Inteligente de Resúmenes en Telegram

**Al-Grano Bot** es un bot de Telegram avanzado diseñado para ayudarte a procesar y entender grandes cantidades de información de manera rápida y eficiente. Ya sea para ponerte al día con conversaciones de chat extensas, resumir vídeos de YouTube, extraer la esencia de artículos web o analizar documentos, Al-Grano Bot te ofrece la información clave "al grano".

## 🌟 Características Principales

### **Resúmenes de Chat Inteligentes**

- Genera resúmenes de los últimos 300 mensajes en un chat grupal
- Ofrece una interfaz de configuración completa con `/configurar_resumen` para personalizar los resúmenes
- Resúmenes diarios automáticos programables

### **Resúmenes de Contenido Específico**

Al responder a un mensaje con `/summarize`, el bot puede procesar:

- **Mensajes de texto**: Resume el contenido del mensaje citado
- **Vídeos de YouTube**: Extrae la transcripción (si está disponible) y la resume
- **Artículos web**: Extrae el contenido principal del artículo y lo resume
- **Mensajes de voz y archivos de audio**: Transcribe el audio usando Whisper y resume la transcripción
- **Vídeos y notas de vídeo de Telegram**: Extrae el audio, lo transcribe con Whisper y resume el contenido
- **Documentos (PDF, DOCX, TXT)**: Extrae el texto del documento y lo resume, con capacidad de procesar documentos grandes mediante estrategia de "map-reduce"

### **Configuración Personalizada por Chat**

El comando `/configurar_resumen` abre un menú interactivo multiidioma para ajustar:

- **🧠 Tono**:

  - Neutral 🧾 - Objetivo y profesional
  - Informal 🙂 - Casual y amigable
  - Sarcástico 😈 - Con ironía y mordacidad
  - **Colega 🗣️** - Como ese amigo sarcástico que te cuenta qué pasó (¡modo exclusivo!)
  - Irónico 🙃 - Señalando contradicciones con inteligencia
  - Absurdo 🤪 - Surrealista con metáforas extrañas

- **📏 Longitud**: Corto (2-3 frases), Medio (5-7 frases), Largo (10-15 frases)
- **🌐 Idioma**: Español 🇪🇸, English 🇺🇸, Français 🇫🇷, Português 🇧🇷
- **👥 Inclusión de Nombres**: Decide si los resúmenes deben mencionar a los participantes
- **⏰ Resúmenes Diarios**: Activa, desactiva y programa resúmenes automáticos (00:00, 03:00, 08:00, 12:00, 18:00, 21:00)

### **Exportación de Chat para IA**

- El comando `/export_chat` genera un archivo `.json` optimizado para análisis por IA
- Incluye metadatos completos, estadísticas de participación, hilos de conversación reconstruidos y transcripción cronológica
- Formato estructurado para facilitar el análisis posterior con herramientas de IA

### **Sistema de Gestión de Uso**

Para usuarios no administradores:

- **Operaciones Simples** (resumir chat, texto, enlaces): Cooldown de 2 minutos
- **Operaciones Avanzadas** (transcribir audio/video, procesar documentos): Cooldown de 10 minutos y límite de 5 usos diarios
- Los administradores del bot no tienen limitaciones
- Tamaño máximo de archivo: 20MB

### **Procesamiento Multimedia Avanzado**

- Integración con **ffmpeg** para compresión de audio (Opus) y extracción de audio de vídeos (WAV PCM)
- Transcripción de alta calidad usando **OpenAI Whisper** (modelo `whisper-1`)
- Soporte para múltiples formatos de audio y video

### **Arquitectura de IA Híbrida**

- **OpenRouter API**: Para generación de resúmenes (modelos como `deepseek/deepseek-r1-0528-qwen3-8b`)
- **OpenAI API directa**: Exclusivamente para transcripción con Whisper
- Sistema de prompts modular y personalizable

### **Características Técnicas Avanzadas**

- **Base de datos SQLite** con limpieza automática de mensajes antiguos
- **Sistema de logging** detallado con manejo de errores global
- **Programador de tareas** (APScheduler) para resúmenes diarios
- **Manejo robusto de errores** con reintentos automáticos para problemas de formato
- **Interfaz multiidioma** completa
- **Decoradores personalizados** para logging, permisos y control de límites

## 🛠️ Tecnologías Utilizadas

### **Core Framework**

- **Python 3.12** - Lenguaje base
- **python-telegram-bot** - Framework del bot
- **aiosqlite** - Base de datos asíncrona SQLite

### **Inteligencia Artificial**

- **OpenRouter API** - Generación de resúmenes con modelos avanzados
- **OpenAI API** - Transcripción de audio con Whisper
- **Sistema de prompts modular** - Configuración flexible de comportamiento de IA

### **Procesamiento de Contenido**

- **ffmpeg** - Procesamiento multimedia
- **youtube-transcript-api** - Transcripciones de YouTube
- **python-readability** - Extracción de contenido web
- **python-docx** - Procesamiento de documentos Word
- **PyPDF2** - Procesamiento de documentos PDF

### **Servicios y Utilidades**

- **APScheduler** - Programación de tareas
- **python-dotenv** - Gestión de variables de entorno
- **pytz** - Manejo de zonas horarias
- **certifi** - Certificados SSL

## 📋 Requisitos Previos

- **Python 3.12** o superior
- **Conda** (recomendado para gestión del entorno)
- **ffmpeg** instalado y accesible en el PATH del sistema
- **Token de bot de Telegram**
- **Clave de API de OpenRouter**
- **Clave de API de OpenAI** (para Whisper)

## 🚀 Configuración e Instalación

### 1. **Clonar el Repositorio**

```bash
git clone https://github.com/mihailmariusiondev/al-grano-bot.git
cd al-grano-bot
```

### 2. **Crear y Activar el Entorno Conda**

```bash
conda env create -f environment.yml
conda activate al-grano-bot
```

### 3. **Configurar Variables de Entorno**

Crea un archivo `.env` en la raíz del proyecto:

```env
# --- OBLIGATORIAS ---
BOT_TOKEN="TU_TOKEN_DE_TELEGRAM"
OPENROUTER_API_KEY="TU_CLAVE_DE_API_DE_OPENROUTER"
OPENAI_API_KEY="TU_CLAVE_DE_API_DE_OPENAI"

# --- OPCIONALES (valores por defecto mostrados) ---
# Administradores del bot (IDs de Telegram separados por comas)
# AUTO_ADMIN_USER_IDS_CSV="ID_USUARIO_1,ID_USUARIO_2"

# Configuración de base de datos
# DB_PATH="bot.db"

# Nivel de logging
# LOG_LEVEL="INFO"

# Configuración OpenRouter
# OPENROUTER_SITE_URL="https://github.com/mihailmariusiondev/al-grano-bot"
# OPENROUTER_SITE_NAME="Al-Grano Bot"
# OPENROUTER_PRIMARY_MODEL="deepseek/deepseek-r1-0528-qwen3-8b:free"
# OPENROUTER_FALLBACK_MODEL="deepseek/deepseek-r1-0528-qwen3-8b"
```

### 4. **Configurar Administradores**

Los usuarios especificados en `AUTO_ADMIN_USER_IDS_CSV` recibirán automáticamente permisos de administrador, eximiéndolos de todos los límites de uso.

## ▶️ Uso

### **Iniciar el Bot**

```bash
python main.py
```

### **Comandos Disponibles**

| Comando               | Descripción                                                                                                                        |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `/start`              | Inicia el bot en el chat y activa la configuración por defecto                                                                     |
| `/help`               | Muestra una guía detallada con todos los comandos y funcionalidades                                                                |
| `/summarize`          | **Comando principal** - Sin responder: resume últimos mensajes del chat<br>Respondiendo a mensaje: resume ese contenido específico |
| `/configurar_resumen` | Abre el menú interactivo de configuración (solo administradores)                                                                   |
| `/export_chat`        | Envía archivo JSON con historial completo optimizado para IA                                                                       |

### **Tipos de Contenido Soportados**

#### **Audio y Video**

- Formatos soportados: MP3, MP4, OGG, WAV, WebM, MOV
- Transcripción automática con OpenAI Whisper
- Compresión inteligente para optimizar procesamiento

#### **Documentos**

- **PDF**: Extracción completa de texto
- **DOCX**: Procesamiento de documentos Word
- **TXT**: Archivos de texto plano
- **Estrategia Map-Reduce**: Para documentos grandes

#### **Web y YouTube**

- **YouTube**: Transcripciones automáticas cuando están disponibles
- **Artículos web**: Extracción inteligente de contenido principal
- **Enlaces**: Procesamiento automático de URLs

### **Sistema de Límites**

#### **Para Usuarios Regulares**

- **Operaciones Simples**: Cooldown de 2 minutos
  - Resumir chat
  - Resumir texto
  - Resumir enlaces web
- **Operaciones Avanzadas**: Cooldown de 10 minutos + 5 usos diarios
  - Transcribir audio/video
  - Procesar documentos

#### **Para Administradores**

- Sin cooldowns
- Sin límites diarios
- Acceso completo a todas las funcionalidades

## 📂 Estructura del Proyecto

```
al-grano-bot/
├── bot/
│   ├── callbacks/              # Lógica de menús interactivos
│   │   └── configure_summary_callback.py
│   ├── commands/               # Comandos del bot
│   │   ├── start_command.py
│   │   ├── help_command.py
│   │   ├── summarize_command.py
│   │   ├── configure_summary_command.py
│   │   ├── export_chat_command.py
│   │   └── message_handler.py
│   ├── handlers/               # Procesadores de contenido
│   │   ├── article_handler.py
│   │   ├── audio_handler.py
│   │   ├── document_handler.py
│   │   ├── video_handler.py
│   │   ├── youtube_handler.py
│   │   └── error_handler.py
│   ├── prompts/                # Sistema de prompts modular
│   │   ├── base_prompts.py
│   │   └── prompt_modifiers.py
│   ├── services/               # Lógica de negocio
│   │   ├── openai_service.py
│   │   ├── database_service.py
│   │   ├── message_service.py
│   │   ├── scheduler_service.py
│   │   └── daily_summary_service.py
│   ├── utils/                  # Utilidades
│   │   ├── constants.py
│   │   ├── decorators.py
│   │   ├── format_utils.py
│   │   ├── logger.py
│   │   ├── media_utils.py
│   │   ├── text_utils.py
│   │   └── get_message_type.py
│   ├── bot.py                  # Lógica principal del bot
│   └── config.py               # Gestión de configuración
├── logs/                       # Archivos de log (generados automáticamente)
├── .env                        # Variables de entorno (crear manualmente)
├── environment.yml             # Definición del entorno Conda
├── main.py                     # Punto de entrada
└── README.md                   # Este archivo
```

## 🔧 Características Técnicas Avanzadas

### **Base de Datos**

- **SQLite** con operaciones asíncronas
- **Limpieza automática** de mensajes antiguos
- **Triggers SQL** para mantenimiento automático
- **Gestión de esquemas** con migraciones automáticas

### **Sistema de Logging**

- **Logs estructurados** con diferentes niveles
- **Rotación automática** de archivos
- **Notificaciones de errores** a administradores

### **Gestión de Memoria**

- **Procesamiento por lotes** para operaciones grandes
- **Limpieza automática** de archivos temporales
- **Optimización** para documentos grandes

### **Seguridad**

- **Validación de archivos** por tipo MIME
- **Límites de tamaño** configurables
- **Sanitización de inputs** para prevenir inyecciones

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Mihail Marius Ion** ([@Arkantos2374](https://t.me/Arkantos2374))

### 💖 Apoyo al Proyecto

Si Al-Grano Bot te resulta útil y quieres apoyar su desarrollo y mantenimiento:

[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/mariusmihailion)

---

## 📊 Estadísticas del Proyecto

- **Idiomas soportados**: 4 (Español, Inglés, Francés, Portugués)
- **Formatos de archivo**: 10+ tipos diferentes
- **Tonos de resumen**: 6 opciones únicas
- **APIs integradas**: OpenRouter + OpenAI
- **Arquitectura**: Modular y escalable
- **Tipo de base de datos**: SQLite con operaciones asíncronas

### 🛠️ Mejoras

#### 🚧 Sistema de Verificación Inteligente (Mejora Futura)

Integrar un flujo de verificación para comprobar afirmaciones en los chats:

1. **Detección de intención**: identificar mensajes que pidan verificar algo. *Recomendación mínima:* expresiones regulares o modelo ligero.
2. **Extracción de la afirmación**: obtener la frase a verificar usando el historial. *Recomendación mínima:* mantener un buffer corto de mensajes.
3. **Reformular la consulta**: convertir la afirmación en una búsqueda web útil. *Recomendación mínima:* plantilla simple o modelo rápido.
4. **Decidir si buscar**: usar un modelo rápido para determinar si es necesario consultar la web. Paso crítico para ganar velocidad.
5. **Buscar en la web**: si procede, obtener 2–3 enlaces (p.ej. de DuckDuckGo). *Recomendación mínima:* scraping directo sin API.
6. **Scraping y limpieza**: extraer solo el texto relevante de cada enlace. *Recomendación mínima:* utilizar `trafilatura`.
7. **Preparar el contexto**: reunir los textos y la pregunta original.
8. **Razonar con la IA**: generar la respuesta final con el modelo elegido.
9. **Responder en Telegram**: enviar la conclusión al usuario, opcionalmente con fuentes.

Este sistema debe funcionar rápidamente y sin depender de APIs de pago.

Consulta [docs/sistema_verificacion_inteligente.md](docs/sistema_verificacion_inteligente.md) para leer la propuesta completa paso a paso.
---
_¡Obtén tus resúmenes al grano con la potencia de la IA! 🚀_
