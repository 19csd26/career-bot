#!/usr/bin/env python3
"""
CareerBot — Telegram Bot powered by Groq (llama-3.1-70b)

Commands:
  /start              — Register + welcome
  /today              — Today's tasks + next problem to solve
  /next               — Next unsolved problem with hint and link
  /week               — Full current week plan
  /progress           — Full progress dashboard
  /log mock           — Log a mock interview
  /log design         — Log a system design session
  /log applied <co>   — Log a company application
  /log solved <lcno>  — Log a solved LeetCode problem
  /log resume         — Mark resume updated
  /log linkedin       — Mark LinkedIn updated
  /log project        — Mark side project deployed
  /log note <text>    — Save a note
  Any other text      — Chat with AI coach (Groq llama-3.1-70b)
"""

import os
import logging
import threading
from datetime import time, date
from http.server import HTTPServer, BaseHTTPRequestHandler
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes,
)

from groq_client import chat as groq_chat
from roadmap import (
    get_today_schedule, get_current_week_plan,
    current_week_number, SYSTEM_PROMPT, TARGET_COMPANIES,
)
from tg_tracker import (
    get_stats, log_activity,
    save_chat_id, load_chat_id,
    load_history, save_history,
)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
IST = ZoneInfo("Asia/Kolkata")


# ─── Formatting helpers ────────────────────────────────────────────────────────

def fmt_today() -> str:
    stats = get_stats()
    schedule = get_today_schedule()
    week_plan = get_current_week_plan()
    solved_ids = {str(p["id"]) for p in stats["solved_problems"]}

    lines = [
        f"📅 *{date.today().strftime('%A, %d %b')} — Week {schedule['week']}: {schedule['theme']}*\n",
        "*Today's Tasks:*",
    ]
    for task in schedule["tasks"]:
        lines.append(f"• {task}")

    problems = week_plan.get("problems", [])
    unsolved = [p for p in problems if str(p["id"]) not in solved_ids]

    lines.append("\n*Next Problem to Solve:*")
    if unsolved:
        p = unsolved[0]
        slug = p["name"].lower().replace(" ", "-").replace("(", "").replace(")", "").replace("/", "")
        lines.append(f"LC {p['id']}. *{p['name']}* `[{p['diff']}]`")
        lines.append(f"💡 Hint: _{p['hint']}_")
        lines.append(f"🔗 https://leetcode.com/problems/{slug}/")
    elif problems:
        lines.append("✅ All this week's problems solved! Move to next week's list.")
    else:
        lines.append("Mock interview week — open [Pramp](https://www.pramp.com) and start a session.")

    lines.append(f"\n*Snapshot:* {stats['total_solved']} solved · {stats['companies_applied']} applied · {stats['mock_interviews']} mocks")
    weeks_left = max(0, 12 - schedule["week"])
    lines.append(f"⏳ {weeks_left} weeks left in the 3-month plan.")
    return "\n".join(lines)


def fmt_next() -> str:
    stats = get_stats()
    week_plan = get_current_week_plan()
    solved_ids = {str(p["id"]) for p in stats["solved_problems"]}
    problems = week_plan.get("problems", [])
    unsolved = [p for p in problems if str(p["id"]) not in solved_ids]

    if not unsolved:
        return "✅ All this week's problems solved\\! Run /week to see what's next."

    p = unsolved[0]
    slug = p["name"].lower().replace(" ", "-").replace("(", "").replace(")", "").replace("/", "")
    return (
        f"🎯 *Next: LC {p['id']}\\. {p['name']}*\n\n"
        f"Difficulty: `{p['diff']}`\n"
        f"💡 Hint: _{p['hint']}_\n\n"
        f"🔗 [Open on LeetCode](https://leetcode.com/problems/{slug}/)\n\n"
        f"After solving, log it with:\n`/log solved {p['id']}`"
    )


def fmt_week() -> str:
    plan = get_current_week_plan()
    stats = get_stats()
    solved_ids = {str(p["id"]) for p in stats["solved_problems"]}

    lines = [
        f"📆 *Week {plan['week']}: {plan['theme']}*\n",
        f"🌅 Morning: {plan['morning_task']}",
        f"🌙 Evening: {plan['evening_task']}",
        f"🏖 Weekend: {plan['weekend_task']}\n",
    ]

    problems = plan.get("problems", [])
    if problems:
        lines.append("*Problems this week:*")
        for p in problems:
            done = "✅" if str(p["id"]) in solved_ids else "⭕"
            lines.append(f"{done} LC {p['id']}\\. {p['name']} `[{p['diff']}]`")
            if str(p["id"]) not in solved_ids:
                lines.append(f"   💡 _{p['hint']}_")
    else:
        lines.append("*Mock interview week* — aim for 3 sessions on Pramp and 2 system design mocks.")

    return "\n".join(lines)


def fmt_progress() -> str:
    stats = get_stats()
    week_num = current_week_number()
    expected = week_num * 5
    status = "✅ On track" if stats["total_solved"] >= expected else f"⚠️ Behind \\(expected ~{expected}\\)"

    solved_list = ""
    if stats["solved_problems"]:
        items = [f"LC {p['id']}" for p in stats["solved_problems"]]
        solved_list = "\n• " + "\n• ".join(items)
    else:
        solved_list = "\nNone yet — start with /next"

    companies = ""
    if stats["companies_list"]:
        items = [c["company"] if isinstance(c, dict) else c for c in stats["companies_list"]]
        companies = "\n• " + "\n• ".join(items)
    else:
        companies = "\nNone yet"

    return (
        f"📊 *Progress Report — Week {week_num}/12*\n\n"
        f"*DSA*\n"
        f"Solved: {stats['total_solved']} problems · {status}\n"
        f"Problems:{solved_list}\n\n"
        f"*Applications & Networking*\n"
        f"Applied to: {stats['companies_applied']} companies{companies}\n"
        f"Mock interviews: {stats['mock_interviews']}\n"
        f"System design sessions: {stats['system_design_sessions']}\n\n"
        f"*Milestones*\n"
        f"{'✅' if stats['resume_updated'] else '⭕'} Resume updated with metrics\n"
        f"{'✅' if stats['linkedin_updated'] else '⭕'} LinkedIn updated\n"
        f"{'✅' if stats['side_project_done'] else '⭕'} Side project deployed\n\n"
        f"*Top Targets \\(not yet applied\\)*\n"
        + "\n".join(
            f"• {c['name']} \\| {c['domain']}"
            for c in TARGET_COMPANIES[:5]
            if c["name"] not in {
                (x["company"] if isinstance(x, dict) else x)
                for x in stats["companies_list"]
            }
        )
    )


def build_ai_context(stats: dict, week_plan: dict) -> str:
    solved = [f"LC {p['id']}" for p in stats["solved_problems"]]
    return (
        f"Current date: {date.today()}\n"
        f"Current week: Week {week_plan['week']} — {week_plan['theme']}\n"
        f"Problems solved: {stats['total_solved']} total — {', '.join(solved) or 'none yet'}\n"
        f"Companies applied: {stats['companies_applied']}\n"
        f"Mock interviews done: {stats['mock_interviews']}\n"
        f"Resume updated: {stats['resume_updated']}\n"
        f"Side project done: {stats['side_project_done']}\n"
    )


# ─── Reminder formatters ───────────────────────────────────────────────────────

def fmt_morning_reminder() -> str:
    stats = get_stats()
    week_plan = get_current_week_plan()
    solved_ids = {str(p["id"]) for p in stats["solved_problems"]}
    problems = week_plan.get("problems", [])
    unsolved = [p for p in problems if str(p["id"]) not in solved_ids]

    msg = (
        f"🌅 *Good morning, Raghav\\!*\n"
        f"Time for your DSA block \\(6:00 – 7:30 AM\\)\n\n"
        f"Week {week_plan['week']}: *{week_plan['theme']}*\n"
        f"Solved so far: {stats['total_solved']} problems\n\n"
    )
    if unsolved:
        p = unsolved[0]
        slug = p["name"].lower().replace(" ", "-").replace("(", "").replace(")", "")
        msg += (
            f"*Solve today:* LC {p['id']}\\. {p['name']} `[{p['diff']}]`\n"
            f"💡 _{p['hint']}_\n"
            f"🔗 [Open problem](https://leetcode.com/problems/{slug}/)\n\n"
            f"Log when done: `/log solved {p['id']}`"
        )
    else:
        msg += "All this week's problems done\\! Do a revision round or start next week's list\\."
    return msg


def fmt_evening_reminder() -> str:
    stats = get_stats()
    week_plan = get_current_week_plan()
    task = week_plan.get("evening_task", "Study system design or work on applications")

    msg = (
        f"🌙 *Evening study block \\(8:00 – 9:30 PM\\)*\n\n"
        f"*Tonight's focus:* {task}\n\n"
    )
    nudges = []
    if not stats["resume_updated"]:
        nudges.append("⚠️ Resume still not updated with metrics — do it tonight")
    if not stats["linkedin_updated"]:
        nudges.append("⚠️ LinkedIn not updated yet")
    if stats["companies_applied"] < 5 and week_plan["week"] >= 4:
        nudges.append(f"⚠️ Only {stats['companies_applied']} applications sent — target is 15–20")
    if nudges:
        msg += "\n".join(nudges)
    return msg


def fmt_weekly_reminder() -> str:
    stats = get_stats()
    week_plan = get_current_week_plan()
    expected = week_plan["week"] * 5
    on_track = stats["total_solved"] >= expected

    return (
        f"📋 *Sunday Weekly Review — Week {week_plan['week']}*\n\n"
        f"Problems solved: {stats['total_solved']} {'✅' if on_track else f'⚠️ behind \\(expected ~{expected}\\)'}\n"
        f"Companies applied: {stats['companies_applied']}\n"
        f"Mock interviews: {stats['mock_interviews']}\n"
        f"System design sessions: {stats['system_design_sessions']}\n\n"
        f"Open your Notion Weekly Review Log and fill in this week's entry\\.\n"
        f"Set your 3 priorities for next week before you close Notion\\."
    )


# ─── Handlers ─────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    save_chat_id(chat_id)
    await update.message.reply_text(
        "👋 *Welcome, Raghav\\!*\n\n"
        "I'm your CareerBot — personal DSA \\+ career coach powered by Groq\\.\n\n"
        "*Commands:*\n"
        "/today — today's plan \\+ next problem\n"
        "/next — next unsolved problem\n"
        "/week — full week schedule\n"
        "/progress — progress dashboard\n"
        "/log — log activity \\(see examples below\\)\n\n"
        "*Logging examples:*\n"
        "`/log solved 217` — mark LC 217 solved\n"
        "`/log applied Razorpay` — log an application\n"
        "`/log mock` — log a mock interview\n"
        "`/log design` — log a system design session\n"
        "`/log resume` — mark resume updated\n\n"
        "*Or just type anything* and I'll coach you\\! 🎯",
        parse_mode="MarkdownV2",
    )


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fmt_today(), parse_mode="Markdown")


async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fmt_next(), parse_mode="MarkdownV2")


async def cmd_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fmt_week(), parse_mode="MarkdownV2")


async def cmd_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fmt_progress(), parse_mode="MarkdownV2")


async def cmd_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage:\n"
            "`/log solved 217` — problem solved\n"
            "`/log applied Razorpay` — applied to company\n"
            "`/log mock` — mock interview done\n"
            "`/log design` — system design session done\n"
            "`/log resume` — resume updated\n"
            "`/log linkedin` — LinkedIn updated\n"
            "`/log project` — side project deployed\n"
            "`/log note <text>` — save a note",
            parse_mode="Markdown",
        )
        return

    sub = args[0].lower()
    detail = " ".join(args[1:])

    mapping = {
        "mock":     ("mock_interview", ""),
        "design":   ("system_design", ""),
        "resume":   ("resume_done", ""),
        "linkedin": ("linkedin_done", ""),
        "project":  ("project_done", ""),
        "applied":  ("company_applied", detail),
        "solved":   ("problem_solved", detail),
        "note":     ("note", detail),
    }

    if sub not in mapping:
        await update.message.reply_text(f"Unknown log type: `{sub}`. Try /log for usage.", parse_mode="Markdown")
        return

    activity_type, activity_detail = mapping[sub]

    if sub in ("applied", "solved", "note") and not detail:
        await update.message.reply_text(f"Please add a detail. E.g. `/log {sub} <value>`", parse_mode="Markdown")
        return

    result = log_activity(activity_type, activity_detail)
    await update.message.reply_text(f"✅ {result}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    stats = get_stats()
    week_plan = get_current_week_plan()
    context_msg = build_ai_context(stats, week_plan)
    history = load_history()

    system_msg = {"role": "system", "content": SYSTEM_PROMPT + "\n\nCURRENT STATUS:\n" + context_msg}
    history.append({"role": "user", "content": user_text})

    await update.message.chat.send_action("typing")
    response = groq_chat([system_msg] + history)

    history.append({"role": "assistant", "content": response})
    save_history(history)

    await update.message.reply_text(response)


# ─── Scheduled Jobs ───────────────────────────────────────────────────────────

async def job_morning(context: ContextTypes.DEFAULT_TYPE):
    chat_id = load_chat_id()
    if chat_id:
        await context.bot.send_message(chat_id=chat_id, text=fmt_morning_reminder(), parse_mode="MarkdownV2")


async def job_evening(context: ContextTypes.DEFAULT_TYPE):
    chat_id = load_chat_id()
    if chat_id:
        await context.bot.send_message(chat_id=chat_id, text=fmt_evening_reminder(), parse_mode="MarkdownV2")


async def job_weekly(context: ContextTypes.DEFAULT_TYPE):
    chat_id = load_chat_id()
    if chat_id:
        await context.bot.send_message(chat_id=chat_id, text=fmt_weekly_reminder(), parse_mode="MarkdownV2")


# ─── Health check server for Railway ──────────────────────────────────────────

class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"CareerBot OK")

    def log_message(self, *args):
        pass


def _start_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    logger.info(f"Health server running on port {port}")
    server.serve_forever()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set. Check your .env file.")

    # Health check server in background (required by Railway)
    threading.Thread(target=_start_health_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()

    # Register commands
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("today",    cmd_today))
    app.add_handler(CommandHandler("next",     cmd_next))
    app.add_handler(CommandHandler("week",     cmd_week))
    app.add_handler(CommandHandler("progress", cmd_progress))
    app.add_handler(CommandHandler("log",      cmd_log))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Schedule reminders (IST timezone)
    jq = app.job_queue
    jq.run_daily(job_morning, time=time(6,  0, tzinfo=IST))   # 6:00 AM IST
    jq.run_daily(job_evening, time=time(20, 0, tzinfo=IST))   # 8:00 PM IST
    jq.run_daily(job_weekly,  time=time(19, 0, tzinfo=IST), days=(6,))  # Sunday 7 PM IST

    logger.info("CareerBot started. Polling for messages...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
