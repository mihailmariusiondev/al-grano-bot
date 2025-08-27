# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate Conda environment
conda env create -f environment.yml
conda activate al-grano-bot

# Required system dependency
# ffmpeg must be installed and available in PATH
```

### Running the Bot
```bash
# Start bot (requires .env configuration)
python main.py

# Environment variables required:
# BOT_TOKEN, OPENROUTER_API_KEY, OPENAI_API_KEY
```

### Development Workflow
```bash
# No formal test suite - manual testing via Telegram
# Check logs for debugging:
tail -f logs/bot.log
tail -f logs/errors.log

# Database inspection (SQLite):
sqlite3 bot.db ".tables"
sqlite3 bot.db "SELECT * FROM telegram_user LIMIT 5;"
```

## Architecture Overview

### Core Architecture Pattern
The bot follows a **layered service architecture** with singleton pattern implementation:

**Singletons**: All major services (`DatabaseService`, `OpenAIService`, `TelegramBot`, `Config`) use singleton pattern to ensure single instance across the application lifecycle.

**Initialization Flow**: `main.py` → Load config → Initialize DB → Initialize AI services → Setup admins → Start bot with scheduler

### Service Layer Structure
```
├── bot/bot.py              # Main TelegramBot singleton, handler registration
├── bot/config.py           # Configuration singleton with env loading  
├── bot/services/           # Business logic services
│   ├── database_service.py # SQLite operations, user/chat/message management
│   ├── openai_service.py   # AI model calls (OpenRouter + OpenAI Whisper)
│   ├── message_service.py  # Telegram message utilities
│   ├── scheduler_service.py # APScheduler for daily summaries
│   └── daily_summary_service.py # Automated summary generation
├── bot/handlers/           # Content processors by media type
├── bot/commands/           # Telegram command implementations
├── bot/callbacks/          # Inline keyboard callback handlers
└── bot/utils/              # Cross-cutting utilities and decorators
```

### AI Model System
**Hybrid API Strategy**: 
- **OpenRouter**: Summary generation with fallback model chain (7 models: Qwen → Kimi → GLM → Gemini → DeepSeek variants)
- **OpenAI Direct**: Whisper transcription only

**Fallback Chain**: Automatically tries next model on rate limits/failures. Models defined in `bot/constants/models.py` with metadata and priorities.

**Prompt System**: Modular prompts in `bot/prompts/` with configurable tone/length/language modifiers applied dynamically per chat settings.

### Database Design
**SQLite** with async operations (`aiosqlite`). Key tables:
- `telegram_user`: User data, admin status, usage limits
- `chat_group`: Chat configurations (tone, length, language, daily summary settings)
- `messages`: Chat message history with auto-cleanup
- `usage_tracking`: Rate limiting and daily usage counters

**Auto-cleanup**: Triggers and scheduled tasks remove old messages and reset daily counters.

### Content Processing Pipeline
**Message Flow**: Command/callback → Handler selection → Content extraction → AI processing → Response formatting

**Media Processing**:
- **Audio/Video**: `ffmpeg` compression → Whisper transcription → Summary
- **Documents**: Text extraction (PDF/DOCX/TXT) with map-reduce for large files
- **Web/YouTube**: Content scraping/transcript API → Summary
- **Chat**: Message aggregation (300 recent) → Summary

### Permission & Rate Limiting System
**Decorator-based**: `@admin_required`, `@rate_limited`, `@usage_limited` decorators in `bot/utils/decorators.py`

**Rate Limits**: 
- Simple operations: 2min cooldown
- Advanced operations (transcription/docs): 10min cooldown + 5 daily limit
- Admins: No limits

**Admin Management**: Auto-admin setup via `AUTO_ADMIN_USER_IDS_CSV` environment variable.

### Configuration Management
**Environment-driven**: All configuration in `.env` file loaded via `bot/config.py` singleton.

**Chat Settings**: Per-chat configuration stored in database with interactive menu system (`/configurar_resumen` command).

### Error Handling & Logging
**Global Error Handler**: `bot/handlers/error_handler.py` catches all unhandled exceptions with admin notifications.

**Structured Logging**: Multiple log files (`bot.log`, `errors.log`) with rotation, different log levels per module.

**Admin Notifications**: Critical errors and rate limit issues automatically notify configured admin users.

### Key Integration Points
**External Dependencies**:
- `python-telegram-bot`: Core bot framework
- `ffmpeg`: Media processing (must be in PATH)
- `APScheduler`: Task scheduling for daily summaries
- `aiosqlite`: Async database operations

**API Integrations**:
- Telegram Bot API (via python-telegram-bot)
- OpenRouter API (summary generation)
- OpenAI API (Whisper transcription)
- YouTube Transcript API (video transcripts)

## Development Notes

### Adding New Content Handlers
1. Create handler in `bot/handlers/`
2. Add prompt template in `bot/prompts/base_prompts.py`
3. Register in summarize command logic
4. Update SummaryType literal in openai_service.py

### Modifying AI Models
- Update `bot/constants/models.py` for model changes
- Fallback order is critical - test thoroughly
- Model metadata used for logging and user display

### Database Schema Changes
- Add migrations in `database_service.py` initialize method
- Consider data migration for existing deployments
- Update cleanup triggers if needed

### Multi-language Support
All user-facing text stored in `bot/constants/messages.py` with language keys. Bot supports Spanish, English, French, Portuguese.