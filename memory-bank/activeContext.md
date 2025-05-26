# Active Context: Al-Grano Bot

## 1. Enfoque de Trabajo Actual

El enfoque de trabajo actual es ejecutar un bloque de tareas interconectadas que refinarán las capacidades del bot y su infraestructura de IA. Estas tareas son:

1.  **Actualizar `HELP_MESSAGE` en `bot/commands/help_command.py`**: Modificar el mensaje de ayuda para eliminar referencias al comando `/about` (diferido), y a las funcionalidades de resumen de fotos y encuestas (eliminadas del alcance).
2.  **Refactorización de Prompts**: Externalizar los prompts del sistema desde `OpenAIService` a un nuevo directorio `bot/prompts/`.
3.  **Refactorización del Sistema de IA**: Migrar el procesamiento de LLM a OpenRouter (usando `deepseek/deepseek-r1:free` o similar) y mantener la API directa de OpenAI exclusivamente para Whisper (transcripción). Esto implica actualizar la configuración de API keys y la lógica en `OpenAIService`.
4.  **Eliminación de Funcionalidades de Fotos y Encuestas**: Remover todo el código asociado al resumen de estos tipos de contenido de la base del código.
5.  **Actualización Completa del Banco de Memoria**: Asegurar que todos los documentos del Memory Bank reflejen con precisión el estado del proyecto después de completar las tareas anteriores y planificar las nuevas (esta operación actual).

**La tarea actual es la "Actualización Completa del Banco de Memoria" (punto 5 de la lista).**
**Una vez completada esta actualización, la siguiente tarea inmediata del bloque será la "Actualización de `HELP_MESSAGE`" (punto 1 de la lista).**

## 2. Cambios Recientes

- **Decisión Estratégica de Refactorización y Enfoque**:
  - Se ha decidido refactorizar el sistema de IA para utilizar OpenRouter con un modelo como `deepseek/deepseek-r1:free` para las tareas de resumen, buscando flexibilidad y optimización de costos.
  - La API directa de OpenAI se usará exclusivamente para las transcripciones con Whisper.
  - Como parte de un reenfoque en las funcionalidades principales de resumen de texto y multimedia, se ha decidido eliminar el soporte para resumir fotos y encuestas.
  - La implementación del comando `/about` se ha diferido indefinidamente.
- **Planificación del Bloque de Trabajo Actual**: Se ha definido el conjunto de 5 tareas (listadas arriba) para implementar estos cambios.
- **Actualización del Banco de Memoria**: Esta misma actividad está en curso para alinear la documentación con estas nuevas directrices y planes.

## 3. Próximos Pasos (Inmediatamente después de esta actualización del Memory Bank)

1.  **Iniciar la Tarea: Actualizar `HELP_MESSAGE` en `bot/commands/help_command.py`**.
    - Abrir el archivo `bot/commands/help_command.py`.
    - Localizar la constante `HELP_MESSAGE`.
    - Modificar el contenido de `HELP_MESSAGE`:
      - Eliminar cualquier mención o descripción del comando `/about`.
      - En la sección que lista los "Tipos de Contenido que el Bot Puede Resumir" (o similar), eliminar "Fotos" (o "Imágenes") y "Encuestas".
      - Asegurar que la explicación del uso del comando `/summarize` (tanto para historial de chat como para mensajes específicos respondidos) no haga referencia a fotos o encuestas como contenido procesable.
      - Verificar que la información sobre límites de uso (cooldowns, cuotas diarias) sea precisa y esté actualizada.
      - Conservar la información de autoría y el enlace de donaciones.
    - Revisar la totalidad del `HELP_MESSAGE` para garantizar su coherencia, claridad y corrección gramatical tras los cambios.
2.  Una vez completada y verificada la actualización de `HELP_MESSAGE`, se procederá con la siguiente tarea del bloque: Refactorización de Prompts.

## 4. Decisiones y Consideraciones Activas

- **Modelo en OpenRouter**: Se utilizará `deepseek/deepseek-r1:free` (o un modelo similar de DeepSeek disponible en OpenRouter) como objetivo inicial para resúmenes.
- **Estructura de Directorio para Prompts**: Se creará `bot/prompts/` y dentro un archivo como `summary_prompts.py` (o `system_prompts.py`) para albergar los prompts del sistema.
- **Impacto de la Eliminación de Funcionalidades**: La eliminación de resúmenes de fotos y encuestas simplificará `summarize_command.py`, `get_message_type.py`, y permitirá la eliminación de `photo_handler.py`.
- **API Keys**: Se requerirán dos claves: `OPENROUTER_API_KEY` y `OPENAI_API_KEY_FOR_WHISPER`.

## 5. Patrones y Preferencias Importantes (Observados y a Mantener/Introducir)

- **Modularidad**: Esencial durante la refactorización de `OpenAIService` y la externalización de prompts. Mantener la separación de responsabilidades.
- **Singletons para Servicios**: Continuar usando este patrón.
- **Manejo Asíncrono**: Crucial.
- **Configuración Externalizada**: Mantener y adaptar para las nuevas API keys (`.env` y `config.py`).
- **Logging Detallado**: Mantener.
- **Claridad del Propósito del Bot**: La eliminación de funcionalidades secundarias (fotos, encuestas) refuerza la identidad de "Al-Grano Bot" como una herramienta especializada en resúmenes de contenido textual y multimedia principal.

## 6. Aprendizajes e Ideas del Proyecto (Recientes)

- La transición a plataformas como OpenRouter puede ofrecer mayor flexibilidad en la elección de modelos de IA y una potencial optimización de costos operativos.
- Enfocar el bot en un conjunto más reducido y central de funcionalidades mejora la calidad y la experiencia del usuario.
- La gestión de prompts es crítica; externalizarlos mejora la mantenibilidad.
