# Al-Grano Telegram Bot

Al-Grano is a Telegram bot designed to summarize various types of content for chat groups. It can generate concise summaries of conversations, YouTube videos, articles, documents, and more.

## Features

- **Chat Summarization**: Summarize recent conversations with `/summarize` command
- **Content Summarization**: Summarize various media types:

  - Text messages
  - YouTube videos (via subtitles)
  - Web articles
  - Documents (PDF, DOCX, TXT)
  - Audio and voice messages
  - Videos and video notes
  - Photos and polls

- **Daily Summary**: Automatically generate daily summaries of chat activity
- **Customizable Summaries**: Toggle between detailed and concise summary formats
- **Premium Features**: Enhanced functionality for premium users
- **Admin Controls**: Special commands for chat administrators

## Commands

- `/start` - Initialize the bot in the chat
- `/help` - Display a detailed help guide
- `/summarize` - Generate summaries of messages or specific content
- `/toggle_daily_summary` - Enable/disable automatic daily chat summaries
- `/toggle_summary_type` - Switch between detailed and concise summary formats

## How to Use

### Summarizing Recent Messages

Send `/summarize` without replying to any message to summarize the last 300 messages in the chat.

### Summarizing Specific Content

Reply to a message with `/summarize` to generate a summary of that specific content, whether it's text, media, or a link.

### YouTube Video Summarization

Reply to a message containing a YouTube link with `/summarize` to get a summary based on the video's subtitles.

## Installation and Setup

1. **Clone the repository**

   ```
   git clone https://github.com/yourusername/al-grano-bot.git
   cd al-grano-bot
   ```

2. **Set up the environment**

   ```
   conda env create -f environment.yml
   conda activate al-grano-bot
   ```

3. **Set up environment variables**
   Create a `.env` file with the following variables:

   ```
   BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   DB_PATH=bot.db
   LOG_LEVEL=INFO
   DEBUG_MODE=false
   ```

4. **Run the bot**
   ```
   python main.py
   ```

## Dependencies

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

## Architecture

The bot uses a modular design:

- Command handlers process user commands
- Media handlers process different content types
- Services manage state, scheduling, and AI integration
- Utilities provide helper functions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you find this bot useful, consider supporting its development.
