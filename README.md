# Al-Grano Telegram Summarization Bot

Al-Grano is a powerful Telegram bot that helps users summarize various types of content, from chat conversations to videos, documents, and web articles. The bot leverages OpenAI's advanced language models to generate concise, informative summaries.

## Features

- **Text Summarization**: Summarize recent chat messages or specific text messages
- **Media Summarization**:

  - YouTube videos (using transcript extraction)
  - Voice messages and audio files
  - Videos and video notes
  - Documents (PDF, DOCX, TXT)
  - Photos (with image analysis)
  - Web articles
  - Polls

- **Daily Summaries**: Automatic daily summaries of chat activity
- **Flexible Summary Types**: Toggle between detailed or concise summary formats
- **User Management**: Premium and admin user management
- **Cooldown System**: Prevent command spam with a configurable cooldown

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/al-grano-bot.git
cd al-grano-bot
```

2. Create and activate the conda environment:

```bash
conda env create -f environment.yml
conda activate al-grano-bot
```

3. Create a `.env` file with your configuration:

```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
DB_PATH=bot.db
LOG_LEVEL=INFO
DEBUG_MODE=false
```

4. Run the bot:

```bash
python main.py
```

## Dependencies

The bot requires:

- Python 3.12
- python-telegram-bot
- openai
- aiosqlite
- youtube-transcript-api
- python-readability
- python-docx
- PyPDF2
- pytz
- APScheduler
- ffmpeg (for audio/video processing)

## Commands

- `/start` - Initialize the bot in the chat
- `/help` - Display the help message with all available commands
- `/summarize` - Generate a summary (can be used as a reply to specific content)
- `/toggle_daily_summary` - Enable or disable automatic daily summaries
- `/toggle_summary_type` - Switch between detailed and concise summary formats

## How to Use

### Summarizing Chat History

Simply send `/summarize` without replying to any message, and the bot will summarize the last 300 messages in the chat.

### Summarizing Specific Content

Reply to any supported content with `/summarize`, and the bot will analyze and summarize that specific content.

### Daily Summaries

Enable daily summaries with `/toggle_daily_summary`. The bot will automatically generate a summary of the previous day's chat activity at 3 AM (Madrid time).

## Project Structure

- `bot/`: Main application code
  - `bot.py`: Bot initialization and configuration
  - `commands/`: Command handlers
  - `handlers/`: Content type handlers
  - `services/`: Core services (OpenAI, database, scheduling)
  - `utils/`: Utility functions and helpers
- `main.py`: Application entry point

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the OpenAI team for providing the API
- Thanks to the python-telegram-bot developers
