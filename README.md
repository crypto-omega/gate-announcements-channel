# Gate.io Announcements Bot

A Python bot that monitors Gate.io announcements and automatically forwards them to a Telegram channel.

## Features

- Monitors Gate.io announcements by checking sequential announcement IDs
- Automatically publishes new announcements to Telegram channel
- Persistent tracking of last processed announcement ID
- Configurable check intervals and retry limits
- Systemd service support for reliable operation
- Automatic restart on failures

## Setup

### Prerequisites

- Python 3.7+
- Telegram Bot Token
- Telegram Channel ID

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gate-announcements-channel
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your configuration:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
MAX_LEFT_ID=5
CHECK_INTERVAL=300
LAST_ANNOUNCEMENT_ID=46450
```

### Configuration

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `TELEGRAM_CHANNEL_ID`: Target Telegram channel ID (format: -1001234567890)
- `MAX_LEFT_ID`: Stop checking after this many consecutive missing announcements (default: 5)
- `CHECK_INTERVAL`: Time between checks in seconds (default: 300 = 5 minutes)
- `LAST_ANNOUNCEMENT_ID`: Starting announcement ID (automatically updated)

## Usage

### Manual Run

```bash
python gate_announcements_bot.py
```

### Systemd Service (Recommended)

Install as a user service:

```bash
./install-service.sh
```

Manage the service:
```bash
# Start the service
systemctl --user start gate-announcements-bot

# Stop the service
systemctl --user stop gate-announcements-bot

# Check status
systemctl --user status gate-announcements-bot

# View logs
journalctl --user -u gate-announcements-bot -f
```

## How It Works

1. The bot reads the last processed announcement ID from `.env`
2. It checks Gate.io for new announcements starting from the next ID
3. For each new announcement found:
   - Extracts the title and URL
   - Sends a formatted message to the Telegram channel
   - Updates the last processed ID in `.env`
4. Stops checking when it encounters 5 consecutive missing announcements
5. Waits for the configured interval before the next check cycle

## Message Format

The bot sends announcements in this format:
```
**Announcement Title**

https://www.gate.com/zh/announcements/article/12345
```

## Dependencies

- `aiohttp` - Async HTTP client for fetching announcements
- `beautifulsoup4` - HTML parsing for extracting announcement titles
- `python-dotenv` - Environment variable management
- `python-telegram-bot` - Telegram Bot API wrapper

## License

MIT License