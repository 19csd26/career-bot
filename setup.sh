#!/bin/bash
# Unified setup for macOS and Linux.
# Installs both the Telegram bot and LeetCode auto-committer as background services.
# Run once: bash setup.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$HOME/.career-bot"
VENV="$REPO_DIR/.venv"

mkdir -p "$LOG_DIR"

# ── Sanity checks ──────────────────────────────────────────────────────────────

if [ ! -f "$REPO_DIR/.env" ]; then
    echo "ERROR: .env file not found."
    echo "Copy .env.example to .env and fill in your keys:"
    echo "  cp .env.example .env"
    exit 1
fi

if [ ! -f "$VENV/bin/python" ]; then
    echo "Virtual environment not found. Creating it..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q -r "$REPO_DIR/requirements.txt"
    echo "Dependencies installed."
fi

# ── OS detection ──────────────────────────────────────────────────────────────

OS="$(uname -s)"

# ── macOS ─────────────────────────────────────────────────────────────────────

install_launchagent() {
    local label="$1"
    local src="$REPO_DIR/$label.plist"
    local dst="$HOME/Library/LaunchAgents/$label.plist"

    launchctl unload "$dst" 2>/dev/null || true
    cp "$src" "$dst"
    launchctl load "$dst"
    echo "  OK  $label (LaunchAgent)"
}

setup_macos() {
    echo "Platform: macOS"
    install_launchagent "com.raghav.career-bot"
    install_launchagent "com.raghav.lc-watcher"
    install_launchagent "com.raghav.index0-watcher"
}

# ── Linux ─────────────────────────────────────────────────────────────────────

install_systemd() {
    local name="$1"
    local src="$REPO_DIR/$name.service"
    local dst="$HOME/.config/systemd/user/$name.service"

    mkdir -p "$HOME/.config/systemd/user"
    sed "s|HOME_DIR|$HOME|g; s|REPO_DIR|$REPO_DIR|g" "$src" > "$dst"

    systemctl --user daemon-reload
    systemctl --user enable "$name"
    systemctl --user restart "$name"
    echo "  OK  $name (systemd user service)"
}

setup_linux() {
    echo "Platform: Linux"

    # Allow services to survive after logout (needed on some distros)
    loginctl enable-linger "$USER" 2>/dev/null || true

    install_systemd "career-bot"
    install_systemd "lc-watcher"
    install_systemd "index0-watcher"
}

# ── Run ───────────────────────────────────────────────────────────────────────

case "$OS" in
    Darwin) setup_macos ;;
    Linux)  setup_linux ;;
    *)
        echo "Unsupported OS: $OS"
        echo "On Windows, run: powershell -ExecutionPolicy Bypass -File setup.ps1"
        exit 1
        ;;
esac

echo ""
echo "All 3 services are running and will auto-start on every login."
echo ""
echo "  career-bot      — Telegram bot"
echo "  lc-watcher      — watches ~/LeetCode, auto-commits to GitHub"
echo "  index0-watcher  — syncs Index 0 completions → ~/LeetCode"
echo ""
echo "Logs:"
echo "  tail -f ~/.career-bot/telegram_bot_error.log"
echo "  tail -f ~/.career-bot/lc_watcher_error.log"
echo "  tail -f ~/.career-bot/index0_watcher_error.log"
echo ""
echo "Next step: open Telegram and send /start to your bot (first time only)."
