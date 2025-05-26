# Product Context: Al-Grano Bot

## 1. Propósito del Proyecto

En la era de la sobrecarga de información, mantenerse al día con las conversaciones en chats grupales, el contenido de vídeos largos o la lectura de documentos extensos puede ser una tarea ardua y que consume mucho tiempo. "Al-Grano Bot" surge como una solución para mitigar este problema, ofreciendo una herramienta inteligente capaz de condensar información diversa en resúmenes fáciles de digerir, yendo "al grano".

El proyecto busca mejorar la eficiencia con la que los usuarios consumen información, permitiéndoles centrarse en lo esencial sin perder el contexto importante. Se enfoca exclusivamente en ser una herramienta de resumen y análisis de contenido directo.

## 2. Problemas que Resuelve

- **Sobrecarga de información en chats**: En grupos de Telegram activos, es fácil perderse puntos clave de la conversación. El bot permite ponerse al día rápidamente.
- **Consumo de tiempo en contenido multimedia**: Ver vídeos de YouTube completos o escuchar largos archivos de audio para extraer la información relevante puede ser ineficiente. El bot proporciona resúmenes y transcripciones.
- **Dificultad para procesar documentos largos**: Leer documentos extensos (PDF, DOCX) para encontrar información específica es tedioso. El bot puede extraer el texto y resumirlo.
- **Necesidad de acceso rápido a la esencia del contenido**: Los usuarios a menudo solo necesitan una idea general de un mensaje, artículo o vídeo antes de decidir si profundizan en él.
- **Uso equitativo de recursos de IA**: Gestionar el acceso a funcionalidades costosas (como transcripciones o análisis de IA complejos) para evitar abusos y controlar costes operativos, implementado a través del sistema de límites del comando `/summarize` y la selección estratégica de modelos de IA (DeepSeek vía OpenRouter para resúmenes, Whisper para transcripciones).

## 3. Cómo Funciona (Experiencia de Usuario Prevista tras Actualizaciones)

- **Interacción Sencilla**: Los usuarios interactúan con el bot principalmente mediante el comando `/summarize` y respondiendo a mensajes. Otros comandos gestionan configuraciones o proveen ayuda.
- **Respuesta Contextual para `/summarize`**:
  - Al enviar `/summarize` sin responder a un mensaje, el bot resume los últimos mensajes del chat (Operación de Texto Simple).
  - Al responder a un mensaje específico con `/summarize`, el bot procesa y resume ese mensaje (texto, enlace a YouTube/artículo web, archivo de audio/video/documento), clasificándolo como Operación de Texto Simple o Contenido Avanzado según corresponda. (El soporte para resumir imágenes/fotos y encuestas ha sido eliminado).
- **Información Progresiva**: El bot envía mensajes de estado ("Procesando...", "Transcribiendo...", etc.) para mantener al usuario informado durante operaciones largas.
- **Resúmenes Claros**: Los resúmenes se presentan en un formato legible, utilizando Markdown para mejorar la estructura.
- **Gestión de Límites para Usuarios Gratuitos (Implementada)**:
  - Los usuarios gratuitos tienen cooldowns entre usos del comando `/summarize`. La duración del cooldown depende de si la tarea es simple (resumir chat/texto: cooldown más corto) o compleja/costosa (resumir audio/video/documento/YouTube: cooldown más largo).
  - Para operaciones complejas/costosas, los usuarios gratuitos tienen un límite diario de usos.
  - El bot informa claramente al usuario si un cooldown está activo o si ha alcanzado su límite diario.
- **Acceso sin Restricciones para Administradores**: Los administradores del bot pueden usar el comando `/summarize` sin cooldowns ni límites diarios.
- **Configuración Personalizada**: Los administradores pueden activar/desactivar resúmenes diarios y elegir entre resúmenes largos o cortos para el chat.
- **Manejo de Errores Amigable**: Si ocurre un error (ej. formato de archivo no soportado, URL inválida), el bot informa al usuario de manera clara.
- **Comandos de Ayuda**: El comando `/help` proporcionará una guía completa sobre cómo usar el bot. (El comando `/about` no será implementado y no aparecerá en la ayuda).
- **Resúmenes Diarios**: Si están activados, los usuarios reciben un resumen de la actividad del chat del día anterior a una hora programada.

## 4. Objetivos de la Experiencia de Usuario (UX)

- **Eficiencia**: Ahorrar tiempo a los usuarios al proporcionarles la esencia del contenido rápidamente.
- **Claridad**: Ofrecer resúmenes que sean fáciles de entender y que capturen los puntos más importantes.
- **Facilidad de Uso**: Asegurar que la interacción con el bot sea intuitiva y no requiera conocimientos técnicos avanzados.
- **Fiabilidad**: El bot debe funcionar de manera consistente y predecible.
- **Utilidad**: Los resúmenes y la información proporcionada deben ser valiosos para el usuario.
- **Equidad y Sostenibilidad**: Implementar un sistema de límites justo para usuarios gratuitos que permita mantener el servicio operativo y gestionar los costes de las APIs de IA. Esto se refuerza con la migración a modelos más costo-efectivos (DeepSeek vía OpenRouter).
- **Transparencia**: Informar claramente a los usuarios sobre cualquier limitación de uso y cambios en funcionalidades (como la eliminación del resumen de fotos/encuestas y la no disponibilidad del comando `/about`).
