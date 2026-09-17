#!/usr/bin/env python3
"""
CareerBot — local Ollama-powered DSA and career coach.
Runs on gemma2:2b via Ollama. Tracks ~/LeetCode progress automatically.

Commands:
  python bot.py today        — Show today's tasks and what to solve next
  python bot.py chat         — Interactive AI coaching session
  python bot.py progress     — Summary of all progress so far
  python bot.py remind       — Send a contextual reminder (used by cron)
  python bot.py log <type>   — Log activity: mock | design | applied <company> | note <text>
  python bot.py week         — Full plan for the current week
  python bot.py next         — Show the next unsolved problem with full hint
"""

import sys
import os
import json
import requests
from datetime import date

# Ensure local imports work regardless of where the script is run from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, CHAT_HISTORY_FILE, BOT_DIR
from roadmap import (
    get_today_schedule, get_current_week_plan, current_week_number,
    SYSTEM_PROMPT, TARGET_COMPANIES
)
from tracker import scan_leetcode_dir, get_stats, log_activity
from notifier import (
    notify, print_banner, print_section,
    morning_reminder, evening_reminder, weekly_reminder
)


# ─── Ollama ───────────────────────────────────────────────────────────────────

def ollama_chat(messages: list[dict]) -> str:
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "Ollama is not running. Start it with: ollama serve"
    except Exception as e:
        return f"Error talking to Ollama: {e}"


def build_context_message(stats: dict, week_plan: dict) -> str:
    solved_names = [f"LC {p['id']}. {p['name']}" for p in stats["solved_in_dir"]]
    return (
        f"Current date: {date.today()}\n"
        f"Current week of plan: Week {week_plan['week']} — {week_plan['theme']}\n"
        f"Problems solved (in ~/LeetCode): {stats['total_solved']} total\n"
        f"Solved problems: {', '.join(solved_names) if solved_names else 'None yet'}\n"
        f"Companies applied to: {stats['companies_applied']}\n"
        f"Mock interviews done: {stats['mock_interviews']}\n"
        f"System design sessions: {stats['system_design_sessions']}\n"
        f"Resume updated with metrics: {stats['resume_updated']}\n"
        f"Side project done: {stats['side_project_done']}\n"
    )


def load_chat_history() -> list[dict]:
    os.makedirs(BOT_DIR, exist_ok=True)
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE) as f:
            return json.load(f)
    return []


def save_chat_history(history: list[dict]):
    os.makedirs(BOT_DIR, exist_ok=True)
    # Keep last 20 exchanges to stay within context limits
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history[-40:], f, indent=2)


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_today():
    stats = get_stats()
    schedule = get_today_schedule()
    week_plan = get_current_week_plan()

    print_banner(f"Today — {date.today().strftime('%A, %d %b %Y')} | Week {schedule['week']}: {schedule['theme']}")

    print_section("Today's Tasks")
    for task in schedule["tasks"]:
        print(f"  • {task}")

    print_section("Next Problem to Solve")
    solved_ids = {p["id"] for p in stats["solved_in_dir"]}
    problems = week_plan.get("problems", [])
    unsolved = [p for p in problems if p["id"] not in solved_ids]

    if unsolved:
        p = unsolved[0]
        print(f"  LC {p['id']}. {p['name']} ({p['diff']})")
        print(f"  Hint: {p['hint']}")
        print(f"  → Open: https://leetcode.com/problems/{p['name'].lower().replace(' ', '-')}/")
    elif problems:
        print("  All this week's problems solved! Great work.")
        print("  Move to next week's list or do a revision round.")
    else:
        print("  Mock interview week. Go to https://www.pramp.com and start a session.")

    print_section("Progress Snapshot")
    print(f"  Problems solved: {stats['total_solved']}")
    print(f"  Applications sent: {stats['companies_applied']}")
    print(f"  Mock interviews: {stats['mock_interviews']}")

    weeks_left = max(0, 12 - schedule["week"])
    print(f"\n  {weeks_left} weeks left in the 3-month plan.")


def cmd_progress():
    stats = get_stats()
    week_num = current_week_number()

    print_banner("Progress Report")

    print_section("DSA")
    print(f"  Total problems solved: {stats['total_solved']}")
    if stats["solved_in_dir"]:
        print("  In ~/LeetCode:")
        for p in stats["solved_in_dir"]:
            print(f"    ✓ LC {p['id']}. {p['name']}")
    expected = week_num * 5
    status = "on track" if stats["total_solved"] >= expected else f"behind (expected ~{expected})"
    print(f"  Status: {status}")

    print_section("Applications & Networking")
    print(f"  Companies applied to: {stats['companies_applied']}")
    print(f"  Mock interviews done: {stats['mock_interviews']}")
    print(f"  System design sessions: {stats['system_design_sessions']}")

    print_section("Milestones")
    print(f"  Resume updated with metrics: {'✓' if stats['resume_updated'] else '✗ — do this this week'}")
    print(f"  LinkedIn updated: {'✓' if stats['linkedin_updated'] else '✗'}")
    print(f"  Side project deployed: {'✓' if stats['side_project_done'] else '✗'}")

    print_section("Top Priority Companies (not yet applied)")
    applied = stats.get("companies_list", [])
    applied_names = {c if isinstance(c, str) else c.get("company", "") for c in applied}
    for co in TARGET_COMPANIES[:5]:
        status = "✓ Applied" if co["name"] in applied_names else f"→ {co['note']}"
        print(f"  {co['name']:20s} | {co['domain']:15s} | {status}")


def cmd_week():
    plan = get_current_week_plan()
    stats = get_stats()
    solved_ids = {p["id"] for p in stats["solved_in_dir"]}

    print_banner(f"Week {plan['week']}: {plan['theme']}")

    print_section("Daily Schedule")
    print(f"  Morning (6:00–7:30 AM): {plan['morning_task']}")
    print(f"  Evening (8:00–9:30 PM): {plan['evening_task']}")
    print(f"  Weekend:                {plan['weekend_task']}")

    if plan["problems"]:
        print_section("This Week's Problems")
        for p in plan["problems"]:
            done = "✓" if p["id"] in solved_ids else "○"
            print(f"  {done} LC {p['id']:4d}. {p['name']:45s} [{p['diff']}]")
            if p["id"] not in solved_ids:
                print(f"       Hint: {p['hint']}")
    else:
        print_section("This Week")
        print("  Mock interview week — no new problems.")
        print("  Complete 3 Pramp sessions and 2 system design mocks.")


def cmd_next():
    stats = get_stats()
    week_plan = get_current_week_plan()
    solved_ids = {p["id"] for p in stats["solved_in_dir"]}
    problems = week_plan.get("problems", [])
    unsolved = [p for p in problems if p["id"] not in solved_ids]

    if not unsolved:
        print("All this week's problems done! Run `python bot.py week` to see next week's list.")
        return

    p = unsolved[0]
    print_banner(f"Next: LC {p['id']}. {p['name']}")
    print(f"Difficulty: {p['diff']}")
    print(f"Hint:       {p['hint']}")
    print(f"URL:        https://leetcode.com/problems/{p['name'].lower().replace(' ', '-').replace('(', '').replace(')', '')}/")
    print()
    print("After solving, create a folder in ~/LeetCode matching the problem name.")
    print("Bot will detect it automatically next time you run any command.")


def cmd_remind(remind_type: str = "general"):
    stats = get_stats()
    week_plan = get_current_week_plan()
    schedule = get_today_schedule()

    if remind_type == "morning":
        morning_reminder(schedule, stats)
    elif remind_type == "evening":
        evening_reminder(schedule, stats)
    elif remind_type == "weekly":
        weekly_reminder(schedule, stats)
    else:
        # General contextual reminder based on time of day
        hour = date.today().timetuple().tm_hour if hasattr(date.today(), 'timetuple') else 12
        import datetime
        hour = datetime.datetime.now().hour
        if hour < 10:
            morning_reminder(schedule, stats)
        elif hour >= 20:
            evening_reminder(schedule, stats)
        else:
            notify("CareerBot", f"Week {schedule['week']}: {schedule['theme']}. Stay on track!")
            cmd_today()


def cmd_log(args: list[str]):
    if not args:
        print("Usage: python bot.py log <type> [detail]")
        print("Types: mock | design | applied <company> | note <text> | resume | linkedin | project")
        return

    activity = args[0]
    detail = " ".join(args[1:]) if len(args) > 1 else ""

    type_map = {
        "mock": "mock_interview",
        "design": "system_design",
        "applied": "company_applied",
        "note": "note",
        "resume": "resume_done",
        "linkedin": "linkedin_done",
        "project": "project_done",
    }

    mapped = type_map.get(activity)
    if not mapped:
        print(f"Unknown log type: {activity}. Use: mock, design, applied, note, resume, linkedin, project")
        return

    if mapped in ("company_applied", "note") and not detail:
        print(f"Please provide detail. E.g.: python bot.py log {activity} 'Razorpay'")
        return

    log_activity(mapped, detail)

    messages = {
        "mock_interview":   "Mock interview logged! Every session sharpens you.",
        "system_design":    "System design session logged! You're building the skill interviewers pay for.",
        "company_applied":  f"Application to {detail} logged! Keep building the pipeline.",
        "note":             f"Note saved: {detail}",
        "resume_done":      "Resume update marked done! Metrics make the difference.",
        "linkedin_done":    "LinkedIn update marked done! Recruiters will start finding you.",
        "project_done":     "Side project marked deployed! Add it to your resume and Notion now.",
    }
    print(f"✓ {messages[mapped]}")


def cmd_chat():
    stats = get_stats()
    week_plan = get_current_week_plan()
    context = build_context_message(stats, week_plan)
    history = load_chat_history()

    system_msg = {"role": "system", "content": SYSTEM_PROMPT + "\n\nCURRENT STATUS:\n" + context}

    print_banner("CareerBot Chat — gemma2:2b")
    print("Your personal DSA + career coach is ready.")
    print("Ask about: today's problem, system design, interview prep, salary negotiation, anything.")
    print("Type 'exit' or press Ctrl+C to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaving chat history. See you tomorrow!")
            save_chat_history(history)
            break

        if user_input.lower() in ("exit", "quit", "bye"):
            save_chat_history(history)
            print("Chat saved. Keep grinding!")
            break

        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        messages = [system_msg] + history
        print("Bot: ", end="", flush=True)
        response = ollama_chat(messages)
        print(response)
        print()

        history.append({"role": "assistant", "content": response})
        save_chat_history(history)


def cmd_help():
    print(__doc__)


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "today"

    commands = {
        "today":    lambda: cmd_today(),
        "progress": lambda: cmd_progress(),
        "week":     lambda: cmd_week(),
        "next":     lambda: cmd_next(),
        "chat":     lambda: cmd_chat(),
        "log":      lambda: cmd_log(args[1:]),
        "remind":   lambda: cmd_remind(args[1] if len(args) > 1 else "general"),
        "help":     lambda: cmd_help(),
    }

    fn = commands.get(cmd)
    if fn:
        fn()
    else:
        print(f"Unknown command: {cmd}")
        cmd_help()


if __name__ == "__main__":
    main()
