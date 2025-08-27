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

### **IA Avanzada con Fallback**

- **Sistema híbrido**: OpenRouter para resúmenes + OpenAI Whisper para transcripciones
- **7 modelos de fallback** automático ante límites de velocidad
- **Prompts personalizables** por tono, idioma y longitud
- **Procesamiento inteligente** con map-reduce para documentos grandes

> 🔧 **Para desarrolladores**: Consulta [CLAUDE.md](CLAUDE.md) para detalles técnicos de arquitectura, patrones de código y guías de desarrollo.

## 🛠️ Stack Tecnológico

**Núcleo**: Python 3.12, python-telegram-bot, SQLite asíncrono
**IA**: OpenRouter API, OpenAI Whisper, sistema de fallback multinivel
**Multimedia**: ffmpeg, YouTube Transcript API, extractores de documentos
**Infraestructura**: APScheduler, logging estructurado, decoradores personalizados

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
# OPENROUTER_MODEL="deepseek/deepseek-r1-0528:free"
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

## 📂 Arquitectura del Proyecto

Arquitectura modular con servicios singleton y manejo asíncrono:

- **`bot/services/`** - Lógica de negocio (base de datos, IA, programador)
- **`bot/handlers/`** - Procesadores especializados por tipo de contenido
- **`bot/commands/`** - Implementaciones de comandos de Telegram
- **`bot/prompts/`** - Sistema de prompts modular y personalizable
- **`main.py`** - Punto de entrada con inicialización de servicios

> 🏗️ **Desarrolladores**: Ver [CLAUDE.md](CLAUDE.md) para detalles completos de arquitectura y patrones de diseño.

## 🔧 Características Técnicas

- **Base de datos inteligente**: SQLite con limpieza automática y migraciones
- **Logging avanzado**: Rotación de archivos y notificaciones de errores
- **Gestión de memoria**: Optimización para documentos grandes
- **Seguridad**: Validación de archivos y sanitización de inputs

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

## 🚀 Roadmap

**Sistema de Verificación Inteligente** - Pipeline automatizado para fact-checking de afirmaciones en chats con búsqueda web y análisis contextual. 

> 📋 Ver [docs/sistema_verificacion_inteligente.md](docs/sistema_verificacion_inteligente.md) para la propuesta técnica completa.
---
_¡Obtén tus resúmenes al grano con la potencia de la IA! 🚀_
