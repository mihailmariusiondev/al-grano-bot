# Progress: Al-Grano Bot

## 1. Funcionalidades Implementadas (Qué Funciona)

Basado en el análisis del código proporcionado, las siguientes funcionalidades están implementadas y se espera que funcionen:

- **Inicialización y Arranque del Bot**:
  - Carga de configuración desde variables de entorno (`Config`).
  - Inicialización de la base de datos SQLite (`DatabaseService`), incluyendo creación de tablas y triggers.
  - Inicialización del cliente de OpenAI (`OpenAIService`).
  - Registro de manejadores de comandos y mensajes (`TelegramBot`).
  - Inicio del polling para recibir actualizaciones de Telegram.
  - Inicio del programador de tareas (`SchedulerService`).
- **Comandos Básicos**:
  - `/start`: Bienvenida al usuario, guarda/actualiza usuario y marca el bot como iniciado en el chat.
  - `/help`: Muestra un mensaje de ayuda detallado.
- **Comando de Resumen (`/summarize`)**:
  - **Resumen de Chat Reciente**: Si se llama sin responder, resume los últimos `MAX_RECENT_MESSAGES` (300) del chat.
    - Maneja el caso de no tener suficientes mensajes (mínimo 5).
  - **Resumen de Mensaje Específico (al responder)**:
    - **Texto Plano**: Resume el texto del mensaje respondido.
    - **Enlace de YouTube**: Extrae la transcripción y la resume (usando `youtube_handler` y `YOUTUBE_REGEX`).
    - **Enlace de Artículo Web**: Extrae el contenido principal del artículo y lo resume (usando `article_handler` y `ARTICLE_URL_REGEX`).
    - **Mensajes de Voz y Archivos de Audio**: Descarga, comprime con `ffmpeg`, transcribe con OpenAI Whisper, y resume la transcripción (usando `audio_handler`).
    - **Vídeos y Notas de Vídeo**: Descarga, extrae audio con `ffmpeg`, comprime el audio, transcribe con Whisper, y resume la transcripción (usando `video_handler`).
    - **Documentos (PDF, DOCX, TXT)**: Descarga, extrae texto (usando `PyPDF2`, `python-docx`), y resume el texto. Implementa una estrategia de chunking y resumen en dos pasos para documentos grandes (`summarize_large_document` en `OpenAIService`).
    - **Imágenes (Fotos)**: Descarga la imagen, la convierte a base64 y la envía a GPT-4o (visión) para análisis y descripción (usando `photo_handler`).
    - **Encuestas**: Formatea la pregunta y opciones de la encuesta para resumirla como texto.
  - Muestra mensajes de progreso durante el procesamiento.
  - Envía mensajes largos divididos en chunks.
- **Gestión de Mensajes**:
  - Todos los mensajes de texto (y captions) se guardan en la base de datos (`message_handler`).
  - Los mensajes antiguos se purgan automáticamente para mantener solo los últimos `MAX_RECENT_MESSAGES`.
- **Resúmenes Diarios**:
  - Comando `/toggle_daily_summary` (admin) para activar/desactivar resúmenes diarios para un chat.
  - `SchedulerService` ejecuta `send_daily_summaries` (de `DailySummaryService`) a las 3 AM (hora de Madrid).
  - `DailySummaryService` genera y envía resúmenes de los mensajes del día anterior a los chats habilitados.
- **Personalización de Resúmenes**:
  - Comando `/toggle_summary_type` (admin) para cambiar entre resúmenes "largos" y "cortos".
  - El tipo de resumen se almacena en `telegram_chat_state` y se usa tanto para `/summarize` (chat reciente) como para resúmenes diarios.
- **Manejo de Usuarios y Permisos**:
  - Creación y actualización de usuarios en la BD (`get_or_create_user`).
  - Decoradores `@admin_command` y `@premium_only` para restringir el acceso a comandos.
  - Los administradores pueden ser definidos en la BD (campo `is_admin`).
- **Utilidades y Soporte**:
  - Sistema de logging robusto (`Logger`).
  - Manejo de errores detallado (`error_handler`), con notificación a administradores.
  - Decorador de cooldown (`@cooldown`) para limitar la frecuencia de uso de comandos (excepto para admins).
  - Decorador `@bot_started` para asegurar que `/start` haya sido usado.

## 2. Qué Queda por Construir (o Mejorar)

- **Gestión de Usuarios Premium Completa**:
  - Actualmente, `@premium_only` restringe el acceso, pero no hay una lógica visible sobre cómo un usuario se _convierte_ en premium (ej. sistema de pago, comando de admin para otorgarlo).
  - Las "funcionalidades avanzadas como resúmenes más detallados y mayor capacidad de procesamiento" mencionadas en el mensaje de `/help` para premium no están explícitamente implementadas de forma diferenciada más allá del acceso. El tipo de resumen (largo/corto) es global por chat, no por usuario.
- **Comando `/about`**: Mencionado en `/help` pero no hay un handler implementado para él en el código proporcionado.
- **Traducción y Localización**: Los prompts de OpenAI están codificados en español. Si se deseara soportar múltiples idiomas, se necesitaría un sistema de internacionalización (i18n).
- **Pruebas Unitarias y de Integración**: No hay archivos de prueba visibles en el código, lo cual es crucial para la mantenibilidad.
- **Interfaz de Administración Más Completa**: Más allá de los comandos individuales, podría haber una interfaz (ej. web o más comandos de bot) para gestionar usuarios (admins, premium), ver estadísticas, etc.
- **Optimización de Costos de OpenAI**: Aunque se usa GPT-4o-mini para chunks de documentos grandes, un análisis continuo de costos y estrategias de prompting podría ser beneficioso.
- **Manejo de Límites de Frecuencia de Telegram más Sofisticado**: El cooldown es por comando; Telegram tiene límites más complejos a nivel de bot.
- **Escalabilidad de la Base de Datos**: SQLite es adecuado para muchos casos, pero para un uso muy intensivo o distribuido, se podría considerar una solución de BD diferente (ej. PostgreSQL).
- **Robustez de `ffmpeg`**: El manejo de errores de `ffmpeg` podría mejorarse, y asegurar su disponibilidad en diferentes entornos de despliegue.

## 3. Estado Actual del Proyecto

- El proyecto parece estar en una fase funcional y relativamente madura en cuanto a las características principales descritas.
- La estructura del código es modular y sigue buenas prácticas generales.
- El bot es capaz de realizar una variedad de tareas de resumen complejas.
- Hay una base sólida para futuras expansiones.

## 4. Problemas Conocidos (Inferidos o Potenciales)

- **Dependencia de la Calidad de Transcripción**: La calidad de los resúmenes de audio/video depende directamente de la calidad de la transcripción de OpenAI Whisper.
- **Dependencia de la Calidad de Extracción de Contenido**: Para artículos web, la calidad depende de `readability`. Para PDFs, de `PyPDF2` (que puede fallar con PDFs complejos o escaneados).
- **Alucinaciones o Imprecisiones de LLM**: Como con cualquier LLM, los resúmenes pueden ocasionalmente contener imprecisiones o "alucinaciones".
- **Manejo de Tiempos de Espera Largos**: Aunque hay mensajes de progreso, operaciones muy largas (ej. procesar un documento enorme o un vídeo muy largo) podrían llevar a timeouts de Telegram o a que el usuario perciba que el bot está colgado si no hay suficiente feedback. El `read_timeout` y `write_timeout` de `ApplicationBuilder` están en 30s.
- **Consumo de Recursos**: El procesamiento de vídeo/audio con `ffmpeg` y las llamadas a OpenAI pueden consumir recursos significativos (CPU, memoria, red, costos de API).

## 5. Evolución de las Decisiones del Proyecto (Inferida)

- **Inicialmente**: Probablemente comenzó con resúmenes de texto simples.
- **Expansión Multimedia**: Se añadieron progresivamente manejadores para YouTube, audio, vídeo, documentos, a medida que se identificaba la necesidad o la viabilidad técnica.
- **Mejora de la Experiencia**: Se introdujeron cooldowns, mensajes de progreso, y un manejo de errores más detallado.
- **Automatización**: Se añadió la funcionalidad de resúmenes diarios mediante `APScheduler`.
- **Personalización**: Se implementó la opción de elegir entre resúmenes largos/cortos.
- **Optimización**: La estrategia para `summarize_large_document` (usando GPT-4o-mini para chunks) sugiere una evolución hacia la optimización de costos/rendimiento para contenido grande.
- **Estructuración**: La adopción de patrones como Singleton para servicios y una clara separación en capas (commands, handlers, services) indica una maduración de la arquitectura del código.
