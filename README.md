# CareerBot — AI Career Coach + LeetCode Auto-Committer

A personal DSA coaching system built for the  journey.  
Runs 24/7 in the background — accessible from your phone via Telegram.

---

## What It Does

| Feature | How |
|---|---|
| Daily DSA reminders (6 AM + 8 PM) | Telegram scheduled messages |
| Weekly review every Sunday | Telegram scheduled message |
| AI coaching chat | Groq API (`openai/gpt-oss-120b`) |
| Today's problem + 12-week roadmap | `/today`, `/week` commands |
| Progress tracking | `/progress` command |
| LeetCode auto-commit to GitHub | Watches `~/LeetCode`, commits + pushes on file save |
| Telegram notification on each solve | Sent by the auto-committer |
| Local CLI bot | Ollama (`gemma2:2b`) — no internet needed |

---

## Prerequisites

| Requirement | macOS | Linux | Windows |
|---|---|---|---|
| Python 3.10+ | `brew install python` | `sudo apt install python3` | [python.org](https://python.org) |
| Git | `brew install git` | `sudo apt install git` | [git-scm.com](https://git-scm.com) |
| Ollama (CLI bot only) | [ollama.com](https://ollama.com) | [ollama.com](https://ollama.com) | [ollama.com](https://ollama.com) |
| Telegram account | — | — | — |

---

## Quick Setup

### Step 1 — Clone the repo

```bash
git clone https://github.com/19csd26/career-bot.git ~/career-bot
cd ~/career-bot
```

### Step 2 — Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
```

**Get your keys:**
- **Telegram bot token** → open Telegram, message [@BotFather](https://t.me/BotFather), send `/newbot`
- **Groq API key** → [console.groq.com](https://console.groq.com) → API Keys → Create

### Step 3 — Install dependencies

```bash
python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Step 4 — Start the background services

**macOS / Linux (Kali, Ubuntu, etc.):**
```bash
bash setup.sh
```

**Windows (run PowerShell as Administrator):**
```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

This installs two background services that **auto-start on every login**:
- `career-bot` — Telegram bot
- `lc-watcher` — LeetCode auto-committer

### Step 5 — Connect Telegram

Open Telegram, find your bot, and send:
```
/start
```

This saves your chat ID so the bot can send you notifications.  
You should get a welcome message immediately.

---

## Platform-Specific Notes

### macOS
Services run as **LaunchAgents** (`~/Library/LaunchAgents/`).

```bash
# Check status
launchctl list | grep raghav

# Restart Telegram bot
launchctl unload ~/Library/LaunchAgents/com.raghav.career-bot.plist
launchctl load ~/Library/LaunchAgents/com.raghav.career-bot.plist

# Restart LeetCode watcher
launchctl unload ~/Library/LaunchAgents/com.raghav.lc-watcher.plist
launchctl load ~/Library/LaunchAgents/com.raghav.lc-watcher.plist
```

### Linux (Kali, Ubuntu, Debian, etc.)
Services run as **systemd user services**.

```bash
# Check status
systemctl --user status career-bot
systemctl --user status lc-watcher

# Restart
systemctl --user restart career-bot
systemctl --user restart lc-watcher

# View logs
journalctl --user -u career-bot -f
journalctl --user -u lc-watcher -f
```

### Windows
Services run in **Task Scheduler** under your user account.

```powershell
# Open Task Scheduler UI
taskschd.msc

# Or manage via PowerShell
Get-ScheduledTask -TaskName "CareerBot-*"
Start-ScheduledTask  -TaskName "CareerBot-TelegramBot"
Stop-ScheduledTask   -TaskName "CareerBot-TelegramBot"
```

---

## Telegram Commands

| Command | What it does |
|---|---|
| `/start` | Register your chat ID (run once) |
| `/today` | Today's tasks + next problem + progress snapshot |
| `/next` | Next unsolved problem with URL and hint |
| `/week` | Full current week plan (all problems + schedule) |
| `/progress` | Full report: DSA stats, applications, milestones |
| `/log mock` | Log a completed mock interview |
| `/log design` | Log a system design practice session |
| `/log applied Razorpay` | Log a job application |
| `/log resume` | Log a resume update |
| Any free text | AI coaching response via Groq |

### Scheduled Reminders

| Time | Message |
|---|---|
| 6:00 AM IST (daily) | Morning DSA reminder + today's problem |
| 8:00 PM IST (daily) | Evening study reminder |
| 7:00 PM IST (Sunday) | Weekly review + next week preview |

---

## LeetCode Auto-Committer

When you solve a problem locally, just save your files — the watcher handles the rest.

**How it works:**
1. You save a file inside `~/LeetCode/121. Best Time to Buy and Sell Stock/`
2. The watcher detects the change
3. After 12 seconds of no activity it auto-commits and pushes to GitHub
4. You receive a Telegram notification

**Folder naming convention** (required):
```
~/LeetCode/
├── 1. Two Sum/
│   ├── two_sum.rb
│   ├── two_sum_traced.rb
│   └── two-sum.md
├── 121. Best Time to Buy and Sell Stock/
│   ├── buy_and_sell_stock.rb
│   ├── buy_and_sell_stock_traced.rb
│   └── best-time-to-buy-and-sell-stock.md
```

Pattern must match: `<number>. <Problem Name>`

```
✓  121. Best Time to Buy and Sell Stock
✗  best-time-to-buy-and-sell-stock    (no number prefix)
✗  LC121                              (wrong format)
```

---

## CLI Bot (Local — Ollama)

For offline use, the CLI bot runs on your local Ollama server.

```bash
# Start Ollama
ollama serve

# Pull the model (first time only)
ollama pull gemma2:2b

# Run commands
source .venv/bin/activate
python bot.py today
python bot.py next
python bot.py week
python bot.py progress
python bot.py chat
```

**Optional alias** — add to `~/.zshrc` or `~/.bashrc`:
```bash
alias bot="$HOME/career-bot/.venv/bin/python $HOME/career-bot/bot.py"
```

Then just use `bot today`, `bot chat`, etc.

---

## View Logs

```bash
# macOS / Linux
tail -f ~/.career-bot/telegram_bot_error.log
tail -f ~/.career-bot/lc_watcher_error.log

# Windows (PowerShell)
Get-Content $env:USERPROFILE\.career-bot\telegram_bot_error.log -Wait
Get-Content $env:USERPROFILE\.career-bot\lc_watcher_error.log -Wait
```

---

## The 12-Week Roadmap

| Weeks | Theme | Goal |
|---|---|---|
| 1–2 | Arrays, Strings, HashMaps, Two Pointers | 30 problems |
| 3–4 | Linked Lists, Stacks, Queues, Binary Search | 30 problems |
| 5–6 | Trees (BFS / DFS / BST), Graphs | 25 problems |
| 7–8 | Dynamic Programming (1D + 2D) | 20 problems |
| 9–10 | Mock interview rounds | 6+ sessions |
| 11–12 | Final applications + offer negotiation | 3 simultaneous offers |

**Daily schedule (parallel to a 10-hour work day):**

| Time | Duration | Activity |
|---|---|---|
| 6:00–7:30 AM | 1.5 hrs | DSA — LeetCode problems |
| 8:00–9:30 PM | 1.5 hrs | System design / applications / study |
| Weekend | 3 hrs/day | Side project, mock interviews, deep work |

---

## Project Structure

```
career-bot/
├── telegram_bot.py          # Telegram bot — commands, AI chat, scheduled reminders
├── lc_watcher.py            # LeetCode file watcher — auto-commit + Telegram notify
├── bot.py                   # Local CLI bot (Ollama)
├── roadmap.py               # 12-week DSA plan + NeetCode problem list
├── tg_tracker.py            # Progress tracker for Telegram bot (data/progress.json)
├── tracker.py               # Progress tracker for CLI bot (scans ~/LeetCode)
├── groq_client.py           # Groq API client for Telegram AI chat
├── notifier.py              # Terminal output formatters
├── config.py                # Paths and model config
│
├── setup.sh                 # Auto-start setup — macOS + Linux
├── setup.ps1                # Auto-start setup — Windows
├── setup_cron.sh            # Cron-based reminders (alternative to LaunchAgent)
│
├── com.raghav.career-bot.plist   # macOS LaunchAgent — Telegram bot
├── com.raghav.lc-watcher.plist   # macOS LaunchAgent — LeetCode watcher
├── career-bot.service            # Linux systemd service — Telegram bot
├── lc-watcher.service            # Linux systemd service — LeetCode watcher
│
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .gitignore               # Excludes .env, data/, .venv/
├── Procfile                 # Railway deployment
└── railway.toml             # Railway config
```

---

## Troubleshooting

**Bot not responding on Telegram:**
```bash
# Check if it's running
launchctl list | grep career-bot          # macOS
systemctl --user status career-bot        # Linux

# View error log
tail -30 ~/.career-bot/telegram_bot_error.log
```

**LeetCode commit not triggering:**
- Make sure the folder name matches the pattern exactly: `121. Best Time to Buy and Sell Stock`
- The watcher waits 12 seconds after the last file save before committing
- Check the log: `tail -f ~/.career-bot/lc_watcher_error.log`

**No Telegram notification after a commit:**
- Make sure you sent `/start` to your bot at least once
- Verify `~/career-bot/data/chat_id.txt` exists and has a number in it

**Groq AI not responding:**
- Check your `GROQ_API_KEY` in `.env`
- Verify the model is available: `GET https://api.groq.com/openai/v1/models`

**Ollama not found (CLI bot):**
```bash
ollama serve
# or open the Ollama app on macOS
```

---

## Built With

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) — Telegram bot framework
- [Groq API](https://console.groq.com) — fast LLM inference for AI chat
- [Ollama](https://ollama.com) — local LLM server for offline CLI bot
- [watchdog](https://github.com/gorakhargosh/watchdog) — cross-platform file system watcher
- macOS LaunchAgent / Linux systemd / Windows Task Scheduler — background service management

---

## License

MIT — do whatever you want with it.
