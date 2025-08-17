# Claude Code Configuration

This file contains instructions for Claude Code to better understand and work with this project.

## Project Overview

This is a Python bot that monitors Gate.io announcements and forwards them to a Telegram channel. The bot uses web scraping to check for new announcements and the Telegram Bot API to send messages.

## Key Files

- `gate_announcements_bot.py` - Main bot application
- `requirements.txt` - Python dependencies
- `.env` - Configuration file (not in git, see .env.example)
- `gate-announcements-bot.service` - Systemd service configuration
- `install-service.sh` - Service installation script

## Development Environment

### Python Dependencies
Run this command to install dependencies:
```bash
pip install -r requirements.txt
```

### Required Dependencies
- aiohttp>=3.8.0 - For async HTTP requests to Gate.io
- beautifulsoup4>=4.11.0 - For parsing HTML content
- python-dotenv>=0.19.0 - For loading environment variables
- python-telegram-bot>=20.0 - For Telegram Bot API

### Environment Variables
The bot requires these environment variables in `.env`:
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `TELEGRAM_CHANNEL_ID` - Target Telegram channel ID  
- `MAX_LEFT_ID` - Max consecutive missing announcements before stopping (default: 5)
- `CHECK_INTERVAL` - Seconds between checks (default: 300)
- `LAST_ANNOUNCEMENT_ID` - Last processed announcement ID (auto-updated)

## Running the Application

### Development
```bash
python gate_announcements_bot.py
```

### Production (Systemd)
```bash
./install-service.sh
systemctl --user start gate-announcements-bot
```

## Testing and Linting

### Running Tests
Currently no test framework is configured. When adding tests, consider using pytest:
```bash
pip install pytest
pytest
```

### Code Linting
To check code quality, install and run linting tools:
```bash
pip install flake8 black
flake8 gate_announcements_bot.py
black gate_announcements_bot.py
```

## Architecture Notes

### Bot Logic Flow
1. Load configuration from `.env` file
2. Read last processed announcement ID
3. Check Gate.io for new announcements (ID + 1 to ID + 10)
4. Parse HTML to extract title and URL
5. Send new announcements to Telegram
6. Update last processed ID in `.env`
7. Wait for configured interval and repeat

### Data Persistence
The bot persists state by updating `LAST_ANNOUNCEMENT_ID` in the `.env` file. This allows the bot to resume from the correct position after restarts.

### Error Handling
- HTTP request failures are logged and retried on next cycle
- Missing announcements don't stop the bot (up to MAX_LEFT_ID consecutive misses)
- Telegram API failures are logged but don't crash the bot
- File I/O errors when updating `.env` are logged

## Monitoring and Logs

### Systemd Logs
```bash
journalctl --user -u gate-announcements-bot -f
```

### Log Levels
- INFO: New announcements found and sent
- WARNING: HTTP errors, missing announcements
- ERROR: Critical failures (Telegram API, file I/O)
- DEBUG: Detailed execution flow (when enabled)

## Security Considerations

- `.env` file contains sensitive tokens and is excluded from git
- Bot token should have minimal permissions (only send messages)
- Channel ID should be validated before deployment
- Consider rate limiting for Telegram API calls

## Deployment Notes

- Bot designed to run as systemd user service
- Automatically restarts on failure
- Logs to systemd journal
- Can be managed with standard systemctl commands
- No root privileges required