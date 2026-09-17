import os

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma2:2b"

LEETCODE_DIR = os.path.expanduser("~/LeetCode")
BOT_DIR = os.path.expanduser("~/.career-bot")
PROGRESS_FILE = os.path.join(BOT_DIR, "progress.json")
CHAT_HISTORY_FILE = os.path.join(BOT_DIR, "chat_history.json")

PLAN_START_DATE = "2026-09-18"
NAME = "Raghav"
CURRENT_CTC = 7
TARGET_CTC = 30
