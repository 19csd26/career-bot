# CareerBot — Local AI Career Coach

> A personal DSA + career coaching bot powered by **Ollama (gemma2:2b)** running entirely on your local machine.
> Built for the **7 LPA → 30 LPA** journey in 3–6 months.

---

## What It Does

- **Tracks your LeetCode progress automatically** by scanning your `~/LeetCode/` folder
- **Tells you exactly what to solve today** based on a 12-week DSA roadmap
- **Sends macOS desktop notifications** at 6 AM (DSA) and 8 PM (study block) via cron
- **AI coaching chat** powered by `gemma2:2b` running locally on Ollama — no API key, no internet needed
- **Tracks applications, mock interviews, and milestones** with simple log commands
- **Salary strategy, negotiation scripts, and company targeting** baked in

---

## Prerequisites

| Requirement | Check | Install |
|---|---|---|
| Python 3.10+ | `python3 --version` | `brew install python` |
| Ollama | `ollama --version` | [ollama.com](https://ollama.com) |
| gemma2:2b model | `ollama list` | `ollama pull gemma2:2b` |
| macOS (for notifications) | — | — |

---

## Setup (Step by Step)

### Step 1 — Clone the repository

```bash
git clone https://github.com/19csd26/career-bot.git
cd career-bot
```

### Step 2 — Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Make sure Ollama is running with gemma2:2b

```bash
# Start Ollama (if not already running as a service)
ollama serve &

# Pull the model if you haven't already
ollama pull gemma2:2b

# Verify it's available
ollama list
```

### Step 5 — Run your first command

```bash
python bot.py today
```

You should see today's tasks, the next problem to solve, and your progress snapshot.

### Step 6 — Set up daily reminders (cron)

This installs 3 cron jobs:
- **6:00 AM** every day — morning DSA reminder with today's problem
- **8:00 PM** every day — evening study reminder
- **7:00 PM every Sunday** — weekly review prompt

```bash
bash setup_cron.sh
```

Verify with:
```bash
crontab -l | grep career-bot
```

---

## All Commands

```bash
# Always activate the venv first (or use the alias below)
source .venv/bin/activate
```

### Daily Use

| Command | What it does |
|---|---|
| `python bot.py today` | Today's tasks + next problem to solve + progress snapshot |
| `python bot.py next` | Next unsolved problem with URL and hint |
| `python bot.py week` | Full plan for the current week (all problems + daily schedule) |
| `python bot.py progress` | Full progress report: DSA, applications, milestones, company targets |
| `python bot.py chat` | Interactive AI coaching session with gemma2:2b |

### Logging Progress

```bash
# After completing a mock interview
python bot.py log mock

# After a system design practice session
python bot.py log design

# After applying to a company
python bot.py log applied "Razorpay"
python bot.py log applied "PhonePe"

# After updating your resume with metrics
python bot.py log resume

# After updating LinkedIn
python bot.py log linkedin

# After deploying your side project
python bot.py log project

# Save a note or observation
python bot.py log note "Struggled with 2D DP today — revisit tomorrow"
```

### Reminders (also called automatically by cron)

```bash
python bot.py remind morning   # Morning DSA reminder
python bot.py remind evening   # Evening study reminder
python bot.py remind weekly    # Sunday weekly review
```

---

## How LeetCode Tracking Works

The bot **automatically scans** your `~/LeetCode/` directory for solved problems.

When you solve a problem, just create a folder named exactly like this:

```
~/LeetCode/
├── 1. Two Sum/
│   ├── two_sum.rb
│   └── two_sum.md
├── 217. Contains Duplicate/
│   ├── contains_duplicate.rb
│   └── contains_duplicate.md
└── ...
```

**No manual logging needed.** The bot will detect new folders automatically on every run.

---

## Shortcut Alias (Optional)

Add this to your `~/.zshrc` to run the bot from anywhere without activating the venv:

```bash
echo 'alias bot="$HOME/career-bot/.venv/bin/python $HOME/career-bot/bot.py"' >> ~/.zshrc
source ~/.zshrc
```

Then use:

```bash
bot today
bot next
bot chat
bot progress
bot log mock
```

---

## The 12-Week Roadmap

| Weeks | Theme | Goal |
|---|---|---|
| 1–2 | Arrays, Strings, HashMaps, Two Pointers | 30 problems |
| 3–4 | Linked Lists, Stacks, Queues, Binary Search | 30 problems |
| 5–6 | Trees (BFS/DFS/BST), Graphs | 25 problems |
| 7–8 | Dynamic Programming (1D + 2D) | 20 problems |
| 9–10 | Mock interview rounds (Pramp / Interviewing.io) | 6+ sessions |
| 11–12 | Final applications + negotiation | 3 simultaneous offers |

**Weekly schedule (parallel to a 10-hour work day):**

| Time Slot | Duration | Activity |
|---|---|---|
| Morning: 6:00–7:30 AM | 1.5 hrs | DSA — LeetCode problems |
| Evening: 8:00–9:30 PM | 1.5 hrs | System design / applications / study |
| Weekend (Sat + Sun) | 3 hrs each | Side project, mock interviews, deep work |
| **Total per week** | **~14 hrs** | Focused prep |

---

## Salary Strategy (7 LPA → 30 LPA)

### Two-Jump Approach

| Jump | Timeline | Target CTC | Companies |
|---|---|---|---|
| Switch #1 | Month 3–4 | 15–20 LPA | Razorpay, PhonePe, CRED, Chargebee, Ather Energy |
| Switch #2 | Month 12–15 | 28–35 LPA | Google, Microsoft, Swiggy, Groww, Zomato |

### 5 Rules to Never Break

1. **Never disclose your current CTC** — say: *"I prefer to discuss based on role budget and market rate"*
2. **Always generate 3 simultaneous offers** — leverage is everything in negotiation
3. **Time your final rounds together** — batch applications so offers land in the same 2-week window
4. **Lead with your niche** — EV + Payments + IoT is rare; FinTech/CleanTech companies pay a premium for it
5. **Never accept the first offer** — counter at 15–20% above; worst case they say no

---

## Project Structure

```
career-bot/
├── bot.py           # Main CLI entry point — all commands live here
├── roadmap.py       # 12-week problem list, weekly plan, Ollama system prompt
├── tracker.py       # Scans ~/LeetCode dir, reads/writes ~/.career-bot/progress.json
├── notifier.py      # macOS desktop notifications + terminal output formatting
├── config.py        # Ollama URL, model name, file paths
├── requirements.txt # Python dependencies (just requests)
├── setup_cron.sh    # Installs 3 cron jobs for daily/weekly reminders
└── README.md        # This file
```

---

## Configuration

Edit `config.py` to change defaults:

```python
OLLAMA_MODEL = "gemma2:2b"      # Change to any model you have in Ollama
LEETCODE_DIR = "~/LeetCode"     # Path to your LeetCode solutions folder
PLAN_START_DATE = "2026-09-18"  # When you started the 12-week plan
```

---

## Troubleshooting

**Bot says "Ollama is not running":**
```bash
ollama serve
# or on macOS, open the Ollama app from Applications
```

**Cron notifications not appearing:**
macOS requires Terminal (or the app running the cron job) to have notification permissions.
Go to: System Settings → Notifications → Terminal → Allow Notifications

**Problems not being detected:**
Make sure your folder name exactly matches the pattern `<number>. <Problem Name>`:
```
✓  217. Contains Duplicate
✗  contains_duplicate        (no number prefix)
✗  LC217-contains-duplicate  (wrong format)
```

**Chat history feels out of context:**
The bot keeps the last 20 exchanges. To start fresh:
```bash
rm ~/.career-bot/chat_history.json
```

---

## Built With

- [Ollama](https://ollama.com) — local LLM server
- [gemma2:2b](https://ollama.com/library/gemma2) — Google's lightweight open model
- Python 3 standard library + `requests`
- macOS `osascript` for desktop notifications
- cron for scheduled reminders

---

## License

MIT — do whatever you want with it.
