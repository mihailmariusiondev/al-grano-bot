# Project Brief: Al-Grano Bot

## 1. Resumen del Proyecto

"Al-Grano Bot" es un bot de Telegram diseñado para proporcionar resúmenes concisos y detallados de diversos tipos de contenido. Su objetivo principal es ayudar a los usuarios a ponerse al día rápidamente con conversaciones en chats grupales, vídeos de YouTube, artículos web, documentos y otros formatos multimedia, ahorrándoles tiempo y esfuerzo.

## 2. Objetivos Principales

- **Resumir Conversaciones de Chat**: Generar resúmenes de los mensajes recientes en un chat de Telegram, permitiendo a los usuarios entender rápidamente los temas discutidos.
- **Resumir Contenido Específico**: Permitir a los usuarios solicitar resúmenes de mensajes individuales, que pueden incluir texto, enlaces, o archivos multimedia.
- **Soporte Multimedia**:
  - Extraer y resumir transcripciones de vídeos de YouTube.
  - Extraer texto y resumir artículos web.
  - Transcribir y resumir mensajes de voz y archivos de audio.
  - Extraer audio, transcribir y resumir contenido de vídeos y notas de vídeo.
  - Extraer texto y resumir documentos (PDF, DOCX, TXT).
  - Analizar y describir imágenes.
  - Resumir encuestas.
- **Resúmenes Diarios Automáticos**: Ofrecer la opción de recibir un resumen diario automático de la actividad del chat.
- **Personalización de Resúmenes**: Permitir a los usuarios elegir entre formatos de resumen largos (detallados) y cortos (concisos).
- **Gestión de Usuarios**: Distinguir entre usuarios normales, usuarios premium y administradores, con diferentes niveles de acceso a funcionalidades.
- **Interfaz Intuitiva**: Proporcionar una experiencia de usuario clara y fácil de usar a través de comandos de Telegram.
- **Persistencia de Datos**: Almacenar mensajes y estados de chat para facilitar la generación de resúmenes y la configuración del bot.

## 3. Alcance del Proyecto

- **Funcionalidades Centrales**:
  - Comandos de inicio (`/start`), ayuda (`/help`).
  - Comando de resumen (`/summarize`) con capacidad para actuar sobre mensajes recientes del chat o mensajes específicos respondidos.
  - Comandos para activar/desactivar resúmenes diarios (`/toggle_daily_summary`).
  - Comandos para cambiar el tipo de resumen (`/toggle_summary_type`).
  - Manejo de diferentes tipos de mensajes (texto, audio, vídeo, documentos, enlaces, imágenes, encuestas).
- **Integraciones**:
  - API de Telegram para la interacción con el bot.
  - API de OpenAI para transcripción de audio, análisis de imágenes y generación de resúmenes.
  - Librerías para procesar archivos (PDF, DOCX), extraer contenido de artículos web y transcripciones de YouTube.
- **Administración**:
  - Comandos restringidos a administradores.
  - Posibilidad de definir usuarios premium con acceso a funcionalidades mejoradas (aunque la lógica específica de "premium" está presente en decoradores, su implementación completa más allá del acceso no está detallada en el código).
- **Persistencia**:
  - Base de datos SQLite para almacenar usuarios, mensajes, y estados de chat.

## 4. Criterios de Éxito (Implícitos)

- El bot responde de manera fiable a los comandos.
- Los resúmenes generados son precisos y útiles.
- El bot maneja correctamente diferentes tipos de contenido.
- Los resúmenes diarios se entregan puntualmente.
- El sistema es estable y maneja los errores de forma adecuada.
