# Project Brief: Al-Grano Bot

## 1. Resumen del Proyecto

"Al-Grano Bot" es un bot de Telegram diseñado para proporcionar resúmenes concisos y detallados de diversos tipos de contenido. Su objetivo principal es ayudar a los usuarios a ponerse al día rápidamente con conversaciones en chats grupales, vídeos de YouTube, artículos web, documentos y otros formatos multimedia, ahorrándoles tiempo y esfuerzo al ir "al grano". El bot se enfoca exclusivamente en esta tarea de resumen y análisis directo de contenido.

## 2. Objetivos Principales

- **Resumir Conversaciones de Chat**: Generar resúmenes de los mensajes recientes en un chat de Telegram.
- **Resumir Contenido Específico**: Permitir a los usuarios solicitar resúmenes de mensajes individuales, que pueden incluir texto, enlaces, o archivos multimedia.
- **Soporte Multimedia para Resumen**:
  - Extraer y resumir transcripciones de vídeos de YouTube.
  - Extraer texto y resumir artículos web.
  - Transcribir y resumir mensajes de voz y archivos de audio.
  - Extraer audio, transcribir y resumir contenido de vídeos y notas de vídeo.
  - Extraer texto y resumir documentos (PDF, DOCX, TXT).
  - Analizar y describir imágenes (con un prompt de análisis fijo).
  - Resumir encuestas.
- **Gestión de Uso Equitativo**: Implementar un sistema de límites (cooldowns, cuotas diarias) para el comando `/summarize` para usuarios gratuitos, diferenciando entre operaciones simples y costosas, mientras se otorga acceso ilimitado a administradores.
- **Resúmenes Diarios Automáticos**: Ofrecer la opción de recibir un resumen diario automático de la actividad del chat.
- **Personalización de Resúmenes**: Permitir a los administradores elegir entre formatos de resumen largos (detallados) y cortos (concisos) para el chat.
- **Interfaz Intuitiva**: Proporcionar una experiencia de usuario clara y fácil de usar a través de comandos de Telegram.
- **Persistencia de Datos**: Almacenar mensajes y estados de chat para facilitar la generación de resúmenes y la configuración del bot, así como los datos de uso de los usuarios para la gestión de límites.

## 3. Alcance del Proyecto

- **Funcionalidades Centrales**:
  - Comandos de inicio (`/start`), ayuda (`/help`), información (`/about` - a implementar).
  - Comando de resumen (`/summarize`) unificado con lógica interna para:
    - Actuar sobre mensajes recientes del chat o mensajes específicos respondidos.
    - Manejar diferentes tipos de mensajes (texto, audio, vídeo, documentos, enlaces, imágenes, encuestas).
    - Aplicar cooldowns y límites diarios para usuarios gratuitos basados en el tipo de operación (simple vs. costosa).
    - Permitir uso ilimitado para administradores.
  - Comandos para activar/desactivar resúmenes diarios (`/toggle_daily_summary` - admin).
  - Comandos para cambiar el tipo de resumen (`/toggle_summary_type` - admin).
- **Integraciones**:
  - API de Telegram.
  - API de OpenAI (transcripción, análisis de imágenes, generación de resúmenes).
  - Librerías para procesar archivos, extraer contenido web y transcripciones de YouTube.
- **Administración**:
  - Comandos restringidos a administradores.
  - Acceso sin límites a funcionalidades para administradores.
- **Persistencia**:
  - Base de datos SQLite para almacenar usuarios (incluyendo estado de admin), mensajes, estados de chat, y datos de uso para la gestión de límites del comando `/summarize`.

## 4. Criterios de Éxito (Implícitos)

- El bot responde de manera fiable a los comandos.
- Los resúmenes generados son precisos y útiles.
- El bot maneja correctamente diferentes tipos de contenido para resumen.
- El sistema de límites y cooldowns para `/summarize` funciona según lo diseñado y es comunicado claramente a los usuarios.
- Los resúmenes diarios se entregan puntualmente.
- El sistema es estable y maneja los errores de forma adecuada.
- Se gestionan eficazmente los costes de API mediante el sistema de límites.
