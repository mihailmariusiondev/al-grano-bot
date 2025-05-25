# Active Context: Al-Grano Bot

## 1. Enfoque de Trabajo Actual

El enfoque principal actual es la **implementación del comando `/summarize` unificado con límites diferenciados por tipo de contenido y nivel de usuario (Administrador vs. Usuario Gratuito)**. Esta es la característica de máxima prioridad.

Esto implica:

- Diseñar y modificar la lógica del comando `/summarize` para que maneje todos los tipos de resúmenes.
- Implementar la distinción entre "Operación de Texto Simple" y "Operación de Contenido Avanzado/Costoso".
- Desarrollar el sistema de cooldowns y límites diarios para usuarios gratuitos.
- Actualizar `DatabaseService` para almacenar y gestionar los datos de uso de los usuarios (tiempos del último uso, contadores diarios, fecha de reseteo del contador).
- Asegurar que los administradores continúen teniendo acceso sin restricciones.
- Refactorizar o eliminar el decorador `@cooldown` actual, ya que su lógica se integrará y expandirá dentro del comando `/summarize`.

## 2. Cambios Recientes

- **Decisión Estratégica Clave**: Se ha decidido separar la funcionalidad de "Modo Compañero de Chat" (el bot participando en conversaciones, siendo mencionado, etc.) en un **bot de Telegram completamente nuevo e independiente**. Esto significa que "Al-Grano Bot" se centrará exclusivamente en su función principal de resumir contenido.
- **Clarificación del Alcance**: Todas las sub-funcionalidades asociadas al "Modo Compañero" (como la interacción con imágenes mediante mención y prompt del usuario, la gestión avanzada de contexto con citas para menciones, la búsqueda web en tiempo real para conversaciones) se han eliminado del alcance de _este_ proyecto (Al-Grano Bot).
- **Priorización**: La característica de límites diferenciados para `/summarize` ha sido establecida como la máxima prioridad.
- **Análisis de Imágenes**: La funcionalidad existente de `/summarize` respondiendo a una imagen (usando `photo_handler` y un prompt de análisis de imagen fijo desde `OpenAIService`) se mantiene y se clasificará como "Operación de Contenido Avanzado/Costoso".

## 3. Próximos Pasos (Desde la perspectiva de Cline)

1.  **Diseño Detallado de la Base de Datos**: Especificar los nuevos campos necesarios en la tabla `telegram_user` o crear una nueva tabla `user_usage_limits` para rastrear:
    - `last_text_simple_op_time` (Timestamp)
    - `last_advanced_op_time` (Timestamp)
    - `advanced_op_today_count` (Entero)
    - `advanced_op_count_reset_date` (Fecha)
2.  **Actualizar `DatabaseService`**: Implementar los métodos para leer, escribir y resetear estos nuevos campos de uso.
3.  **Refactorizar `summarize_command.py`**:
    - Integrar la lógica de identificación del tipo de usuario (Admin/Gratuito).
    - Implementar la clasificación de la operación (Simple/Avanzado).
    - Añadir la lógica de comprobación y aplicación de cooldowns y límites diarios.
    - Asegurar que se llame al handler de contenido apropiado (`chat_history`, `audio_handler`, `video_handler`, etc.).
    - Gestionar la actualización de los contadores de uso en la base de datos.
4.  **Revisar y Actualizar `message_handler.py` y otros handlers de comandos/mensajes** para asegurar la coherencia con los nuevos cambios y la eliminación del decorador `@cooldown` si es reemplazado.
5.  **Actualizar la documentación del Banco de Memoria (`progress.md`, etc.)** para reflejar estos cambios y el nuevo enfoque. (Este paso se está realizando ahora).
6.  **Considerar pruebas** para la nueva lógica de límites.

## 4. Decisiones y Consideraciones Activas

- **Valores Específicos para Límites**: Definir los valores exactos para los cooldowns (ej. 120s, 600s) y el límite diario (ej. 5 operaciones avanzadas).
- **Mensajes al Usuario**: Redactar mensajes claros y concisos para informar a los usuarios sobre los cooldowns y límites alcanzados. Se pueden reutilizar y adaptar los `COOLDOWN_REPLIES` para el mensaje de cooldown.
- **Reset del Contador Diario**: Implementar la lógica para que el `advanced_op_today_count` se resetee a 0 cuando `advanced_op_count_reset_date` sea anterior al día actual.

## 5. Patrones y Preferencias Importantes (Observados y a Mantener/Introducir)

- **Modularidad**: Mantener la separación de responsabilidades (comandos, handlers, servicios).
- **Singletons para Servicios**: Continuar usando este patrón.
- **Manejo Asíncrono**: Sigue siendo crucial.
- **Configuración Externalizada**: Mantener.
- **Logging Detallado**: Mantener y asegurar que la nueva lógica de límites se loguee adecuadamente.
- **Base de Datos SQLite**: Sigue siendo la elección. La nueva lógica de límites aumentará la interacción con `DatabaseService`.
- **Tipado Estático**: Mantener.
- **Claridad del Propósito del Bot**: La separación del "Modo Compañero" refuerza la identidad de "Al-Grano Bot" como una herramienta de resumen.

## 6. Aprendizajes e Ideas del Proyecto (Recientes)

- La funcionalidad de un bot puede crecer hasta el punto de que es mejor dividirla en productos separados para mantener la claridad y la UX.
- Implementar un sistema de límites de uso es una forma de gestionar los costes de API y asegurar un uso equitativo, especialmente antes de tener un sistema de monetización completo.
