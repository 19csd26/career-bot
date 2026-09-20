#!/usr/bin/env python3
"""
LeetCode Auto-Committer
Watches ~/LeetCode for new/modified problem folders.
When files settle (no changes for 12s), auto-commits and pushes to GitHub.
Also sends a Telegram notification and updates career progress tracker.

Run: python lc_watcher.py
Stop: Ctrl+C
"""

import os
import re
import sys
import time
import logging
import threading
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv(Path(__file__).parent / ".env")

LEETCODE_DIR  = Path.home() / "LeetCode"
CAREER_BOT    = Path(__file__).parent
DEBOUNCE_SECS = 12       # wait this long after last file activity before committing
PROBLEM_RE    = re.compile(r"^(\d+)\.\s+(.+)$")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("lc-watcher")


# ─── Git helpers ──────────────────────────────────────────────────────────────

def git(*args) -> tuple[int, str]:
    result = subprocess.run(
        ["git"] + list(args),
        cwd=LEETCODE_DIR,
        capture_output=True,
        text=True,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def has_staged_changes() -> bool:
    _, out = git("diff", "--cached", "--name-only")
    return bool(out.strip())


# ─── Telegram notification ────────────────────────────────────────────────────

def send_telegram(message: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_file = CAREER_BOT / "data" / "chat_id.txt"
    if not token or not chat_file.exists():
        return
    chat_id = chat_file.read_text().strip()
    if not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10,
        )
    except Exception:
        pass


# ─── Commit logic ─────────────────────────────────────────────────────────────

def commit_problem(folder_name: str):
    m = PROBLEM_RE.match(folder_name)
    if not m:
        return

    lc_id        = m.group(1)
    problem_name = m.group(2).strip()
    folder_path  = LEETCODE_DIR / folder_name

    if not folder_path.exists():
        log.warning(f"Folder gone before commit: {folder_name}")
        return

    log.info(f"Staging {folder_name} ...")
    code, out = git("add", f"{folder_name}/")
    if code != 0:
        log.error(f"git add failed: {out}")
        return

    if not has_staged_changes():
        log.info("Nothing new to commit — skipping.")
        return

    log.info(f"Committing: {problem_name}")
    code, out = git("commit", "-m", problem_name)
    if code != 0:
        log.error(f"git commit failed: {out}")
        return

    log.info(f"Pushing to GitHub ...")
    code, out = git("push", "origin", "main")
    if code != 0:
        log.error(f"git push failed: {out}")
        return

    log.info(f"Done! LC {lc_id}. {problem_name} is live on GitHub.")

    # Update career progress tracker
    try:
        sys.path.insert(0, str(CAREER_BOT))
        from tg_tracker import log_activity
        log_activity("problem_solved", lc_id)
        log.info(f"Progress tracker updated: LC {lc_id} marked solved.")
    except Exception as e:
        log.warning(f"Could not update tracker: {e}")

    # Telegram notification
    send_telegram(
        f"✅ *LC {lc_id}. {problem_name}* committed to GitHub!\n\n"
        f"Check it: github.com/19csd26/LeetCode\n\n"
        f"Keep the streak going 🔥"
    )


# ─── File system handler ──────────────────────────────────────────────────────

class LeetCodeHandler(FileSystemEventHandler):
    def __init__(self):
        self._pending: dict[str, float] = {}
        self._lock    = threading.Lock()
        # Start background debounce thread
        threading.Thread(target=self._debounce_loop, daemon=True).start()

    def _problem_folder(self, path: str) -> str | None:
        try:
            rel = Path(path).relative_to(LEETCODE_DIR)
        except ValueError:
            return None
        parts = rel.parts
        if not parts:
            return None
        top = parts[0]
        # Ignore .git, .DS_Store, hidden files
        if top.startswith(".") or top == "__pycache__":
            return None
        return top if PROBLEM_RE.match(top) else None

    def on_any_event(self, event):
        if event.is_directory:
            return
        folder = self._problem_folder(event.src_path)
        if not folder:
            return
        with self._lock:
            self._pending[folder] = time.monotonic()

    def _debounce_loop(self):
        while True:
            time.sleep(2)
            now       = time.monotonic()
            to_commit = []
            with self._lock:
                for folder, last_t in list(self._pending.items()):
                    if now - last_t >= DEBOUNCE_SECS:
                        to_commit.append(folder)
                        del self._pending[folder]
            for folder in to_commit:
                log.info(f"No activity for {DEBOUNCE_SECS}s — auto-committing {folder}")
                commit_problem(folder)


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    if not LEETCODE_DIR.exists():
        log.error(f"LeetCode directory not found: {LEETCODE_DIR}")
        sys.exit(1)

    log.info(f"Watching {LEETCODE_DIR}")
    log.info(f"Auto-commit triggers {DEBOUNCE_SECS}s after last file save.")
    log.info("Press Ctrl+C to stop.\n")

    handler  = LeetCodeHandler()
    observer = Observer()
    observer.schedule(handler, str(LEETCODE_DIR), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Stopping watcher...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
