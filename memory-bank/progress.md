# Progress: Al-Grano Bot

## 1. Funcionalidades Implementadas (Qué Funciona Actualmente - Antes del Próximo Bloque de Trabajo)

- **Inicialización y Arranque del Bot**: Carga de config (actualmente con `OPENAI_API_KEY` que será reemplazada), DB, `OpenAIService` (actualmente con GPT-4o/mini para resúmenes y Whisper vía API directa OpenAI), registro de handlers, scheduler.
- **Comandos Básicos**: `/start`, `/help` (mensaje de ayuda actual incluye `/about`, fotos, encuestas, que serán modificados).
- **Comando de Resumen (`/summarize`) Unificado con Límites Diferenciados**:
  - Funciona con niveles de usuario (admin/gratuito) y tipos de operación (Texto Simple/Contenido Avanzado) aplicando cooldowns y límites diarios.
  - **Soporte de Contenido Actual**: Texto, enlaces YouTube/artículo, audio/voz, vídeo, documentos (PDF, DOCX, TXT). (El soporte para imágenes/fotos y encuestas, aunque presente en el código actual, será eliminado).
  - Mensajes de progreso y manejo de mensajes largos.
- **Gestión de Mensajes**: Guardado y purga de mensajes.
- **Resúmenes Diarios**: Comando `/toggle_daily_summary`, servicio y scheduler funcionan.
- **Personalización de Resúmenes**: Comando `/toggle_summary_type` funciona.
- **Manejo de Usuarios y Permisos**: Creación/actualización de usuarios, `@admin_command`, admins automáticos.

## 2. Qué Queda por Construir (o Mejorar)

### **TAREAS PRIORITARIAS (Bloque de Trabajo Actual)**

Este es el bloque de tareas actualmente planificado y en el que se centrará el desarrollo:

1.  **Actualizar `HELP_MESSAGE` en `bot/commands/help_command.py`**:
    - **Descripción**: Modificar `HELP_MESSAGE` para eliminar referencias al comando `/about` (cuya implementación se difiere), y a las funcionalidades de resumen de fotos y encuestas (que serán eliminadas del alcance del proyecto). Asegurar que la descripción de `/summarize` y los límites de uso sea precisa con los tipos de contenido soportados restantes.
    - **Estado**: **PENDIENTE**
2.  **Refactorización de Prompts**:
    - **Descripción**: Mover todas las definiciones de prompts del sistema (actualmente en `OpenAIService.SUMMARY_PROMPTS`) a un nuevo módulo dedicado, por ejemplo, `bot/prompts/summary_prompts.py`. Actualizar `OpenAIService` para importar y utilizar estos prompts externalizados.
    - **Estado**: **PENDIENTE**
3.  **Refactorización del Sistema de IA**:
    - **Descripción**:
      - Modificar el acceso a los modelos de lenguaje (LLM) para que utilicen la API de OpenRouter, con el objetivo de usar `deepseek/deepseek-r1:free` (o un modelo similar de DeepSeek) para todas las tareas de resumen.
      - Mantener el uso de la API directa de OpenAI exclusivamente para el modelo Whisper-1 (transcripción de audio).
      - Actualizar las variables de entorno (`.env`) y la configuración (`bot/config.py`) para manejar dos claves de API: `OPENROUTER_API_KEY` y `OPENAI_API_KEY_FOR_WHISPER` (reemplazando la actual `OPENAI_API_KEY`).
      - Refactorizar `OpenAIService` para instanciar y utilizar dos clientes `openai.AsyncOpenAI` (uno para OpenRouter, otro para OpenAI directa) según la tarea.
      - Ajustar constantes relacionadas con tokens (ej. `MAX_INPUT_CHARS`) para alinearlas con las capacidades del modelo de DeepSeek seleccionado.
    - **Estado**: **PENDIENTE**
4.  **Eliminación de Funcionalidades de Fotos y Encuestas**:
    - **Descripción**: Eliminar completamente el código relacionado con el resumen de imágenes (fotos) y encuestas. Esto incluye:
      - Modificar `summarize_command.py` para quitar los casos de manejo de `photo` y `poll`.
      - Eliminar el archivo `bot/handlers/photo_handler.py` y su importación.
      - Actualizar `bot/utils/get_message_type.py` para remover "photo" y "poll" de `MessageType` y de la lógica de detección.
      - Revisar y eliminar mensajes de error, progreso o variables específicas de estas funcionalidades en todo el código.
    - **Estado**: **PENDIENTE**
5.  **Actualización Completa del Banco de Memoria**:
    - **Descripción**: Revisar y actualizar todos los archivos del Memory Bank (`projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`, `progress.md`, `activeContext.md`) para reflejar con precisión los cambios implementados y las nuevas decisiones del proyecto tras completar las tareas anteriores de este bloque, o al inicio de un nuevo bloque de trabajo.
    - **Estado**: **EN PROGRESO (Esta misma actualización forma parte de esta tarea continua)**

### **OTRAS FUNCIONALIDADES PENDIENTES (Post-Bloque Actual)**

(Estas tareas se considerarán después de completar el bloque prioritario actual) 6. **Soporte Multi-idioma Completo**: - Tareas: Mecanismo de selección de idioma, internacionalización de mensajes, adaptación de prompts. 7. **Pruebas Automatizadas (Unitarias y de Integración)**. 8. **Funcionalidades Premium y Gestión de Usuarios Avanzada**: - Tareas: Sistema de suscripciones, beneficios premium (si se decide implementar). 9. **Capacidades Avanzadas de Procesamiento (Ej. RAG para documentos)**: - Tareas: Evaluar e implementar RAG para mejorar el resumen de documentos largos si es necesario. 10. **Mejoras Generales de la Plataforma y UX**: - Tareas: Interfaz de administración mejorada (si se considera necesario), optimizaciones de rendimiento.

## 3. Estado Actual del Proyecto

- El proyecto es funcional con las características descritas en la sección "Funcionalidades Implementadas", aunque está a punto de sufrir una refactorización importante.
- **Se ha tomado la decisión de iniciar un bloque de trabajo significativo (los 5 puntos listados como TAREAS PRIORITARIAS) que incluye:**
  1.  Refactorizar el backend de IA para usar OpenRouter con DeepSeek (o similar) para resúmenes y la API directa de OpenAI para Whisper.
  2.  Externalizar los prompts del sistema.
  3.  Eliminar las funcionalidades de resumen de fotos y encuestas para enfocar el bot.
  4.  Actualizar el mensaje de ayuda (`/help`) para reflejar estos cambios y diferir la implementación del comando `/about`.
  5.  Mantener el Banco de Memoria actualizado (esta tarea).
- La estructura del código es modular, lo que debería facilitar estas refactorizaciones.
- **Esta actualización del Memory Bank tiene como objetivo documentar este nuevo plan y estado.**

## 4. Problemas Conocidos (Inferidos o Potenciales)

- **Dependencia de Calidad de Transcripción/Extracción**: La calidad de los resúmenes de audio/video depende de la precisión de Whisper; la de artículos/YouTube de la calidad de extracción de las librerías.
- **Alucinaciones de LLM**: Inherente a los LLM, se evaluará el comportamiento del modelo DeepSeek (o el elegido en OpenRouter).
- **Tiempos de Espera Largos**: Para operaciones muy costosas (documentos muy largos, videos largos). Los mensajes de progreso ayudan a mitigar la percepción.
- **Gestión de Costes de API**: La migración a OpenRouter/DeepSeek busca optimizar esto. El sistema de límites para usuarios gratuitos sigue siendo el mecanismo principal de control.
- **Ausencia de Pruebas Automatizadas**: Incrementa el riesgo de regresiones durante las refactorizaciones. Su implementación es una tarea pendiente importante post-bloque actual.
- **Impacto de la Refactorización**: El cambio en el sistema de IA (`OpenAIService`, config, prompts) es central y requerirá pruebas manuales cuidadosas hasta que se implementen pruebas automatizadas.
