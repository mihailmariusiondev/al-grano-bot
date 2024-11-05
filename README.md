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
