#!/bin/bash
# Sets up the LeetCode auto-committer as a macOS LaunchAgent.
# It will start automatically on login and stay running in background.
# Run once: bash setup_watcher.sh

PLIST_SRC="$HOME/career-bot/com.raghav.lc-watcher.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.raghav.lc-watcher.plist"
LOG_DIR="$HOME/.career-bot"

mkdir -p "$LOG_DIR"

# Unload old version if running
launchctl unload "$PLIST_DST" 2>/dev/null

# Install plist
cp "$PLIST_SRC" "$PLIST_DST"

# Load and start
launchctl load "$PLIST_DST"

echo ""
echo "LeetCode auto-committer is now running!"
echo ""
echo "What it does:"
echo "  - Watches ~/LeetCode for new/modified files"
echo "  - Auto-commits + pushes to github.com/19csd26/LeetCode"
echo "  - Sends you a Telegram notification"
echo "  - Updates your career progress tracker"
echo "  - Starts automatically every time you log in"
echo ""
echo "Logs:   tail -f ~/.career-bot/lc_watcher.log"
echo "Stop:   launchctl unload ~/Library/LaunchAgents/com.raghav.lc-watcher.plist"
echo "Start:  launchctl load ~/Library/LaunchAgents/com.raghav.lc-watcher.plist"
