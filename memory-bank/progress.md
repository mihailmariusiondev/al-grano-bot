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
- **Comando de Resumen (`/summarize`) - Lógica Actual (Pre-Refactor de Límites)**:
  - **Resumen de Chat Reciente**: Si se llama sin responder, resume los últimos `MAX_RECENT_MESSAGES` (300) del chat.
  - **Resumen de Mensaje Específico (al responder)**:
    - Texto Plano, Enlace de YouTube, Enlace de Artículo Web.
    - Mensajes de Voz y Archivos de Audio (descarga, compresión, transcripción, resumen).
    - Vídeos y Notas de Vídeo (descarga, extracción audio, compresión, transcripción, resumen).
    - Documentos (PDF, DOCX, TXT) (descarga, extracción texto, resumen con chunking para grandes).
    - Imágenes (Fotos) (descarga, conversión a base64, análisis con GPT-4o visión y prompt fijo).
    - Encuestas.
  - Muestra mensajes de progreso.
  - Envía mensajes largos divididos.
  - Aplica un decorador de cooldown general (`@cooldown(60)`).
- **Gestión de Mensajes**:
  - Mensajes de texto (y captions) se guardan en la BD (`message_handler`).
  - Mensajes antiguos se purgan.
- **Resúmenes Diarios**:
  - Comando `/toggle_daily_summary` (admin) para activar/desactivar.
  - `SchedulerService` ejecuta `send_daily_summaries`.
- **Personalización de Resúmenes**:
  - Comando `/toggle_summary_type` (admin) para cambiar entre "largos" y "cortos".
- **Manejo de Usuarios y Permisos**:
  - Creación/actualización de usuarios (`get_or_create_user`).
  - Decorador `@admin_command` para restringir comandos.
- **Utilidades y Soporte**:
  - Logging (`Logger`), manejo de errores (`error_handler`), decoradores `@log_command`, `@bot_started`.

## 2. Qué Queda por Construir (o Mejorar) - Enfoque Actual de "Al-Grano Bot"

### **MÁXIMA PRIORIDAD ACTUAL**

1.  **Implementar Comando `/summarize` Unificado con Límites Diferenciados**:
    - **Descripción**: Refactorizar el comando `/summarize` para que sea el único punto de entrada para todos los resúmenes.
    - **Niveles de Usuario**:
      - Administrador: Acceso completo y sin restricciones.
      - Usuario Gratuito: Cooldowns y límites diarios según el tipo de operación.
    - **Tipos de Operación**:
      - "Texto Simple" (resumen de chat, texto plano): Cooldown corto, sin límite diario.
      - "Contenido Avanzado/Costoso" (audio, vídeo, documentos, imágenes, YouTube, artículos): Cooldown largo, límite diario estricto (ej. 5/día).
    - **Tareas**:
      - Modificar la lógica de `summarize_command.py` para incluir la verificación de tipo de usuario, tipo de operación y aplicación de límites.
      - Actualizar `DatabaseService` para almacenar y gestionar `last_text_simple_op_time`, `last_advanced_op_time`, `advanced_op_today_count`, `advanced_op_count_reset_date` por usuario.
      - Integrar la lógica de reseteo del contador diario.
      - Reemplazar o integrar la funcionalidad del decorador `@cooldown` actual.

### **OTRAS FUNCIONALIDADES PENDIENTES (Para "Al-Grano Bot")**

2.  **Funcionalidades Premium y Gestión de Usuarios (Post-MVP de Límites Diferenciados)**:
    - **Sistema de Suscripciones Premium**: Para ofrecer a los usuarios una forma de eliminar/aumentar los límites de uso gratuito. Incluye potencial integración con pasarelas de pago.
    - **Beneficios Premium**: Acceso a modelos de IA más potentes para resúmenes, configuraciones de resumen más detalladas por defecto, etc.
3.  **Capacidades Avanzadas de Procesamiento de Información para Resúmenes (Futuro)**:
    - **Retrieval-Augmented Generation (RAG) para Resumen de Documentos Específicos**: Permitir que `/summarize` (para usuarios premium) utilice RAG sobre documentos previamente "registrados" por el usuario para resúmenes más precisos o Q&A contextual.
4.  **Funcionalidades Multimedia y Generativas Adicionales (Enfocadas en Resumen)**:
    - **Respuestas por Voz (TTS) para Resúmenes**: Opción para entregar resúmenes también como mensajes de voz.
5.  **Mejoras Generales de la Plataforma**:
    - **Soporte Multi-idioma Completo**: Para la interacción y los resúmenes.
    - **Interfaz de Administración Mejorada**: Para gestión de usuarios, límites, estadísticas.
    - **Pruebas Automatizadas (Unitarias y de Integración)**: Crítico para la mantenibilidad.
    - **Implementación del Comando `/about`**: Crear el handler para `/about`.

### **Fuera del Alcance de "Al-Grano Bot" (Planificado para un Bot Separado)**:

- Modo "Compañero de Chat" (bot participando activamente en conversaciones mediante menciones).
- Interacción con imágenes mediante mención y prompt del usuario.
- Gestión avanzada de contexto con citas para menciones.
- Capacidades de búsqueda web en tiempo real para conversaciones.
- Modos de razonamiento avanzado para conversaciones.
- Generación de imágenes independiente mediante comandos como `/create_image`.

## 3. Estado Actual del Proyecto

- El proyecto está en una fase funcional para sus capacidades de resumen actuales.
- Se ha tomado una decisión estratégica importante para **separar las funcionalidades de "asistente conversacional" en un nuevo bot**, manteniendo "Al-Grano Bot" enfocado en resúmenes.
- La **prioridad actual es refactorizar el comando `/summarize` para implementar un sistema de límites diferenciados** para usuarios gratuitos y administradores, lo que implica cambios significativos en la lógica del comando y en la base de datos.
- La estructura del código es modular y adecuada para la expansión planificada.

## 4. Problemas Conocidos (Inferidos o Potenciales)

- **Complejidad de la Nueva Lógica de Límites**: El sistema de cooldowns y límites diarios añade complejidad al comando `/summarize` y a la gestión de datos de usuario.
- **Dependencia de Calidad de Transcripción/Extracción**: Sigue siendo un factor.
- **Alucinaciones de LLM**: Inherente a los LLM.
- **Tiempos de Espera Largos**: Para operaciones muy costosas, a pesar de los mensajes de progreso.
- **Consumo de Recursos y Costes de API**: La nueva lógica de límites busca gestionar esto mejor para usuarios gratuitos.
