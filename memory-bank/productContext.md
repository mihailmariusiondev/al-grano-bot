# Product Context: Al-Grano Bot

## 1. Propósito del Proyecto

En la era de la sobrecarga de información, mantenerse al día con las conversaciones en chats grupales, el contenido de vídeos largos o la lectura de documentos extensos puede ser una tarea ardua y que consume mucho tiempo. "Al-Grano Bot" surge como una solución para mitigar este problema, ofreciendo una herramienta inteligente capaz de condensar información diversa en resúmenes fáciles de digerir.

El proyecto busca mejorar la eficiencia con la que los usuarios consumen información, permitiéndoles centrarse en lo esencial sin perder el contexto importante.

## 2. Problemas que Resuelve

- **Sobrecarga de información en chats**: En grupos de Telegram activos, es fácil perderse puntos clave de la conversación. El bot permite ponerse al día rápidamente.
- **Consumo de tiempo en contenido multimedia**: Ver vídeos de YouTube completos o escuchar largos archivos de audio para extraer la información relevante puede ser ineficiente. El bot proporciona resúmenes y transcripciones.
- **Dificultad para procesar documentos largos**: Leer documentos extensos (PDF, DOCX) para encontrar información específica es tedioso. El bot puede extraer el texto y resumirlo.
- **Barrera del idioma (implícito)**: Aunque los prompts están en español, la capacidad de resumir contenido en un idioma específico (español por defecto según los prompts) puede ayudar a usuarios que prefieren consumir información en ese idioma.
- **Necesidad de acceso rápido a la esencia del contenido**: Los usuarios a menudo solo necesitan una idea general de un mensaje, artículo o vídeo antes de decidir si profundizan en él.

## 3. Cómo Debería Funcionar (Experiencia de Usuario)

- **Interacción Sencilla**: Los usuarios interactúan con el bot mediante comandos de Telegram estándar.
- **Respuesta Contextual**:
  - Al enviar `/summarize` sin responder a un mensaje, el bot resume los últimos mensajes del chat.
  - Al responder a un mensaje específico con `/summarize`, el bot procesa y resume ese mensaje (texto, enlace, archivo, etc.).
- **Información Progresiva**: El bot envía mensajes de estado ("Procesando...", "Transcribiendo...", etc.) para mantener al usuario informado durante operaciones largas.
- **Resúmenes Claros**: Los resúmenes se presentan en un formato legible, utilizando Markdown para mejorar la estructura (títulos, listas).
- **Configuración Personalizada**: Los usuarios (administradores en el código actual) pueden activar/desactivar resúmenes diarios y elegir entre resúmenes largos o cortos.
- **Manejo de Errores Amigable**: Si ocurre un error (ej. formato de archivo no soportado, URL inválida), el bot informa al usuario de manera clara.
- **Comandos de Ayuda**: El comando `/help` proporciona una guía completa sobre cómo usar el bot.
- **Resúmenes Diarios**: Si están activados, los usuarios reciben un resumen de la actividad del chat del día anterior a una hora programada.

## 4. Objetivos de la Experiencia de Usuario (UX)

- **Eficiencia**: Ahorrar tiempo a los usuarios al proporcionarles la esencia del contenido rápidamente.
- **Claridad**: Ofrecer resúmenes que sean fáciles de entender y que capturen los puntos más importantes.
- **Facilidad de Uso**: Asegurar que la interacción con el bot sea intuitiva y no requiera conocimientos técnicos avanzados.
- **Fiabilidad**: El bot debe funcionar de manera consistente y predecible.
- **Utilidad**: Los resúmenes y la información proporcionada deben ser valiosos para el usuario.
- **Engagement (Implícito por el tono)**: El tono informal y "canalla" de algunos mensajes (ej. `START_MESSAGE`, `COOLDOWN_REPLIES`) busca una experiencia de usuario más distintiva y entretenida, aunque esto debe usarse con cuidado para no alienar a los usuarios.
