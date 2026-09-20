#!/bin/bash
# Sets up the Telegram career bot as a macOS LaunchAgent.
# It will start automatically on login and stay running in background.
# Run once: bash setup_bot.sh

PLIST_SRC="$HOME/career-bot/com.raghav.career-bot.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.raghav.career-bot.plist"
LOG_DIR="$HOME/.career-bot"

mkdir -p "$LOG_DIR"

# Unload old version if running
launchctl unload "$PLIST_DST" 2>/dev/null

# Install plist
cp "$PLIST_SRC" "$PLIST_DST"

# Load and start
launchctl load "$PLIST_DST"

echo ""
echo "Telegram career bot is now running!"
echo ""
echo "What it does:"
echo "  - Responds to /today, /next, /week, /progress, /log"
echo "  - Sends morning reminder at 6:00 AM IST"
echo "  - Sends evening reminder at 8:00 PM IST"
echo "  - Sends weekly review every Sunday at 7:00 PM IST"
echo "  - Starts automatically every time you log in"
echo ""
echo "Logs:   tail -f ~/.career-bot/telegram_bot_error.log"
echo "Stop:   launchctl unload ~/Library/LaunchAgents/com.raghav.career-bot.plist"
echo "Start:  launchctl load ~/Library/LaunchAgents/com.raghav.career-bot.plist"
