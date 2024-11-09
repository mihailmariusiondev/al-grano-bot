# Telegram Bot Template in Python

This is a template for creating a Telegram bot using Python. It is designed to be easily extensible and customizable for various purposes.

## Features

- Basic command handling (/start, /help, /about)
- Text message handling
- Detailed error logging
- Integration with OpenAI API for audio transcription and text generation
- Logging configuration for monitoring and debugging

## Requirements

- Python 3.12
- Telegram account
- Telegram bot token
- OpenAI API key

## Initial Setup

To customize this template for your own Telegram bot, follow these steps:

1. **Obtain Credentials**:

   - **Telegram Bot Token**: Create a bot using BotFather and get the token.
   - **OpenAI API Key**: Sign up at OpenAI and generate an API key.

2. **Set Environment Variables**:

   - Create a `.env` file in the project root with the following:
     ```plaintext
     BOT_TOKEN=your_telegram_bot_token
     OPENAI_API_KEY=your_openai_api_key
     ```

3. **Modify Handlers**:

   - Customize messages and logic in the handler files (`bot/handlers/`) to fit your desired functionalities.

4. **Configure Logging**:

   - Adjust logging settings in `bot/utils/logging_config.py` as needed.

5. **Update Dependencies**:

   - Add any additional libraries to `environment.yml` and update the environment with:
     ```bash
     conda env update --file environment.yml
     ```

6. **Change Environment Name**:

   - In `environment.yml`, change the environment name to something specific for your project:
     ```yaml
     name: your-environment-name
     ```

7. **Review Configurations**:
   - Ensure any additional settings in `config/constants.py` (if present) are adjusted to your needs.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/repo-name.git
   cd repo-name
   ```

2. Create a virtual environment with Conda:
   ```bash
   conda env create -f environment.yml
   conda activate your-environment-name
   ```

## Usage

To start the bot, follow these steps:

1. Ensure you are in the project directory.

2. Activate the virtual environment if not already active:

   ```bash
   conda activate your-environment-name
   ```

3. Run the main script:

   ```bash
   python main.py
   ```

4. The bot should now be running. Interact with it on Telegram using commands `/start`, `/help`, and `/about`.

5. To stop the bot, press Ctrl+C in the terminal.

## Project Structure

- `bot/`: Contains the main bot logic
  - `handlers/`: Command and message handlers
  - `services/`: Services for transcription and OpenAI
  - `utils/`: Utilities for configuration and logging
- `main.py`: Application entry point

## Starting a New Project

To start a new project with this template, follow these steps:

1. **Clone the Repository**:

   - Clone the template repository to your local machine.

   ```bash
   git clone https://github.com/your-username/telegram-bot-template.git
   cd telegram-bot-template
   ```

2. **Rename the Project**:

   - Optionally, rename the directory to reflect your new project's name.

   ```bash
   mv telegram-bot-template your-new-project
   cd your-new-project
   ```

3. **Configure the Environment**:

   - Follow the initial setup instructions to customize the bot.

4. **Version Control**:

   - Initialize a new Git repository if you want to track changes.

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

5. **Deploy**:
   - Once satisfied with local testing, consider deploying your bot to a server or cloud service for continuous operation.

## Contributing

Contributions are welcome. Please open an issue to discuss major changes before submitting a pull request.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## TODO

Best strategy for summarising recent messages (summarising in chunks, etc.) and HOW to implement it

- If not chunking, how many messages to summarize at a time?
- Which model to use for summarization? Note: my best options are gpt-4o and gpt-4o-mini, and they have a limit of 128k tokens.
- How to handle max tokens?
- If chunking, how many messages to summarize at a time?
- How to handle quoted messages?
- Should I handle media messages? (I'm not sure if it's a good idea to summarize media messages)
- How to handle long messages?
- Am I missing anything?





Estoy pensando en la siguiente estrategia para resumir los últimos mensajes:
- Para empezar, no sé cuál sería la manera ideal de resumir una conversación de telegram. ¿Resumir todos los mensajes? (esto seguro que es inviable) ¿Resumir los últimos 300 mensajes? ¿Por qué los últimos 300 y no los 100 o los 500? ¿Por qué no los últimos N mensajes? ¿Qué hacemos con mensajes anteriores? ¿Los olvidamos? ¿Qué hacemos con mensajes ya resumidos? ¿Los incluimos en el resumen?
- Supongamos que resumimos los últimos 300 mensajes.
- Por defecto, se arrastran también los mensajes de voz (no audio, ojo) y los video_note para resumir, porque digamos que suelen formar parte de una conversación (quizá esto no sea buena idea y solo se hagan el resumen de texto)
- Los mensajes de voz y video_note se transcriben a texto primero
- El límite de caracteres para un mensaje es de 4096 caracteres.
- El modelo gpt-4o-mini puede resumir 128k tokens, es decir, unos 31250 caracteres.
- Podriamos coger tanta cantidad de mensajes como hagan falta para llegar a esos 31250 caracteres (hay que tener en cuenta que los mensajes de voz y video_note se transcriben a texto primero, así que habrá que ver cuántos caracteres suponen).
- Una vez llegados a los 31250 caracteres, se hace un resumen usando gpt-4o-mini.
- Lo que no sé es cómo pasarle el modelo el mejor contexto posible para que haga un resumen coherente, hay que tener en cuenta que los usuarios pueden responder a un mensaje con otro mensaje, al igual que se puede responder a un mensaje con un mensaje de voz o video_note, supongo que habrá que darle un prompt para que haga un resumen coherente. ¿Cómo podría pasarle el contexto de la mejor manera posible para que el modelo entienda que tiene que hacer un resumen coherente?
- Ejemplo de contexto: "El usuario X dijo blablabla, el usuario Y respondió blablabla, después el usuario X dijo blablabla y el usuario Y respondió blablabla". ¿Sería esto suficiente para que el modelo haga un resumen coherente? ¿Qué otras estrategias podría usar?
- De momento estamos lidiando con un solo resumen (chunk), habrá que ver cómo conseguir no perder contexto si se hace un resumen de N chunks (porque esos ya estarán resumidos).
- Se le pasa el resumen del chunk anterior como contexto para que tenga en cuenta lo que ya se ha resumido.
- ¿Qué hacemos si hay muy pocos mensajes? ¿Cómo se hace el resumen o qué estrategia usamos?
- ¿Estoy pasando algo por alto? ¿Hay alguna otra estrategia que no se me ocurre?