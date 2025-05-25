# Progress: Al-Grano Bot

## 1. Funcionalidades Implementadas (Qué Funciona)

Basado en el análisis del código proporcionado, las siguientes funcionalidades están implementadas y se espera que funcionen:

- **Inicialización y Arranque del Bot**:
  - Carga de configuración desde variables de entorno (`Config`).
  - Inicialización de la base de datos SQLite (`DatabaseService`), incluyendo creación de tablas, triggers y los nuevos campos de usuario para límites.
  - Inicialización del cliente de OpenAI (`OpenAIService`).
  - Registro de manejadores de comandos y mensajes (`TelegramBot`).
  - Inicio del polling para recibir actualizaciones de Telegram.
  - Inicio del programador de tareas (`SchedulerService`).
- **Comandos Básicos**:
  - `/start`: Bienvenida al usuario, guarda/actualiza usuario y marca el bot como iniciado en el chat.
  - `/help`: Muestra un mensaje de ayuda detallado.
- **Comando de Resumen (`/summarize`) Unificado con Límites Diferenciados**:
  - **Punto de Entrada Único**: Todos los tipos de resúmenes se gestionan a través del comando `/summarize`.
  - **Niveles de Usuario**:
    - **Administrador**: Acceso completo y sin restricciones a todas las funcionalidades de resumen. La verificación se realiza mediante `user_db.get("is_admin", False)`.
    - **Usuario Gratuito**: Cooldowns y límites diarios se aplican según el tipo de operación.
  - **Tipos de Operación y Límites Aplicados (para Usuarios Gratuitos)**:
    - **"Texto Simple" (`OPERATION_TYPE_TEXT_SIMPLE`)**:
      - **Activación**: Resumen de historial de chat (sin `reply_to_message`), resumen de mensajes de texto plano (que no sean enlaces a YouTube/artículos), resumen de encuestas.
      - **Cooldown**: `COOLDOWN_TEXT_SIMPLE_SECONDS` (120 segundos). Controlado por `last_text_simple_op_time` en la BD.
      - **Límite Diario**: No aplica.
    - **"Contenido Avanzado/Costoso" (`OPERATION_TYPE_ADVANCED`)**:
      - **Activación**: Resumen de enlaces de YouTube, artículos web, mensajes de voz, archivos de audio, vídeos, notas de vídeo, documentos (PDF, DOCX, TXT), imágenes (fotos).
      - **Cooldown**: `COOLDOWN_ADVANCED_SECONDS` (600 segundos). Controlado por `last_advanced_op_time` en la BD.
      - **Límite Diario**: `DAILY_LIMIT_ADVANCED_OPS` (5 operaciones). Controlado por `advanced_op_today_count` y `advanced_op_count_reset_date` en la BD. El contador se resetea diariamente.
  - **Lógica de Identificación de Tipo de Operación**: Implementada en `summarize_command.py` basada en la presencia de `reply_to_message` y el tipo de contenido del mensaje respondido.
  - **Manejo de Contenido Específico (invocado por `/summarize` tras pasar los límites)**:
    - Texto Plano, Enlace de YouTube, Enlace de Artículo Web.
    - Mensajes de Voz y Archivos de Audio (descarga, compresión, transcripción, resumen).
    - Vídeos y Notas de Vídeo (descarga, extracción audio, compresión, transcripción, resumen).
    - Documentos (PDF, DOCX, TXT) (descarga, extracción texto, resumen con chunking para grandes).
    - Imágenes (Fotos) (descarga, conversión a base64, análisis con GPT-4o visión y prompt fijo).
    - Encuestas.
  - **Mensajes de Progreso y Estado**: Implementados (`update_progress`, `PROGRESS_MESSAGES`).
  - **Envío de Mensajes Largos Divididos**: Utiliza `send_long_message`.
  - **Mensajes Claros para Límites**: Informa al usuario sobre cooldowns activos (`MSG_COOLDOWN_ACTIVE`) y límites diarios alcanzados (`MSG_DAILY_LIMIT_REACHED`).
- **Gestión de Mensajes**:
  - Mensajes de texto (y captions) se guardan en la BD (`message_handler`).
  - Mensajes antiguos se purgan.
- **Resúmenes Diarios**:
  - Comando `/toggle_daily_summary` (admin) para activar/desactivar.
  - `SchedulerService` ejecuta `send_daily_summaries`.
- **Personalización de Resúmenes**:
  - Comando `/toggle_summary_type` (admin) para cambiar entre "largos" y "cortos".
- **Manejo de Usuarios y Permisos**:
  - Creación/actualización de usuarios (`get_or_create_user`), incluyendo campos para la gestión de límites.
  - Decorador `@admin_command` para restringir comandos (no usado en `/summarize` ya que la lógica de admin está integrada).
  - Configuración de administradores automáticos vía `AUTO_ADMIN_USER_IDS_CSV` y un ID por defecto.
- **Utilidades y Soporte**:
  - Logging (`Logger`), manejo de errores (`error_handler`), decoradores `@log_command`, `@bot_started`.

## 2. Qué Queda por Construir (o Mejorar) - Enfoque Actual de "Al-Grano Bot"

### **OTRAS FUNCIONALIDADES PENDIENTES (Para "Al-Grano Bot")**

1.  **Implementación del Comando `/about`**:
    - **Descripción**: Crear el handler para el comando `/about` que muestre información sobre el bot, su propósito y su creador (ya definida en `HELP_MESSAGE` pero necesita su propio comando).
    - **Tareas**:
      - Crear `bot/commands/about_command.py`.
      - Definir un mensaje para `/about`.
      - Registrar el `CommandHandler` en `bot/bot.py`.
2.  **Soporte Multi-idioma Completo**:
    - **Descripción**: Permitir que los usuarios interactúen con el bot y reciban resúmenes en diferentes idiomas.
    - **Tareas**:
      - Mecanismo para que el usuario seleccione/configure su idioma preferido (ej. comando `/language`).
      - Almacenar preferencia de idioma en `telegram_user` o `telegram_chat_state`.
      - Modificar `OpenAIService` y los prompts para usar el idioma seleccionado dinámicamente.
      - Internacionalizar todos los mensajes del bot (ayuda, errores, progreso, confirmaciones).
3.  **Funcionalidades Premium y Gestión de Usuarios (Post-MVP)**:
    - **Sistema de Suscripciones Premium**: Para ofrecer a los usuarios una forma de eliminar/aumentar los límites de uso gratuito. Incluye potencial integración con pasarelas de pago.
    - **Beneficios Premium**: Acceso a modelos de IA más potentes para resúmenes, configuraciones de resumen más detalladas por defecto, etc.
4.  **Capacidades Avanzadas de Procesamiento de Información para Resúmenes (Futuro)**:
    - **Retrieval-Augmented Generation (RAG) para Resumen de Documentos Específicos**: Permitir que `/summarize` (para usuarios premium) utilice RAG sobre documentos previamente "registrados" por el usuario para resúmenes más precisos o Q&A contextual.
5.  **Funcionalidades Multimedia y Generativas Adicionales (Enfocadas en Resumen)**:
    - **Respuestas por Voz (TTS) para Resúmenes**: Opción para entregar resúmenes también como mensajes de voz.
6.  **Mejoras Generales de la Plataforma**:
    - **Interfaz de Administración Mejorada**: Para gestión de usuarios, límites, estadísticas (más allá de los comandos actuales y la config por env).
    - **Pruebas Automatizadas (Unitarias y de Integración)**: Crítico para la mantenibilidad.

### **Fuera del Alcance de "Al-Grano Bot" (Planificado para un Bot Separado)**:

- Modo "Compañero de Chat" (bot participando activamente en conversaciones mediante menciones).
- Interacción con imágenes mediante mención y prompt del usuario.
- Gestión avanzada de contexto con citas para menciones.
- Capacidades de búsqueda web en tiempo real para conversaciones.
- Modos de razonamiento avanzado para conversaciones.
- Generación de imágenes independiente mediante comandos como `/create_image`.

## 3. Estado Actual del Proyecto

- El proyecto está en una fase funcional robusta para sus capacidades de resumen.
- **El refactor del comando `/summarize` para implementar un sistema de límites diferenciados para usuarios gratuitos y administradores está completo y funcional.** Esto ha sido la prioridad principal reciente.
- Se ha tomado una decisión estratégica importante para **separar las funcionalidades de "asistente conversacional" en un nuevo bot**, manteniendo "Al-Grano Bot" enfocado en resúmenes.
- La estructura del código es modular y adecuada para la expansión planificada.
- La siguiente funcionalidad de baja complejidad a abordar es la implementación del comando `/about`.

## 4. Problemas Conocidos (Inferidos o Potenciales)

- **Dependencia de Calidad de Transcripción/Extracción**: Sigue siendo un factor externo.
- **Alucinaciones de LLM**: Inherente a los LLM.
- **Tiempos de Espera Largos**: Para operaciones muy costosas, a pesar de los mensajes de progreso.
- **Gestión de Costes de API**: El sistema de límites implementado es el mecanismo principal de gestión para usuarios gratuitos. Se monitorizará su efectividad.
- **Ausencia de Pruebas Automatizadas**: Incrementa el riesgo de regresiones al añadir nuevas funcionalidades.
