"""
Telegram-specific progress tracker.
Stores all data in ./data/progress.json (no ~/LeetCode dir scanning).
Users log solved problems via /log solved <number>.
"""
import json
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
CHAT_FILE = os.path.join(DATA_DIR, "chat_id.txt")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load() -> dict:
    _ensure_dir()
    if not os.path.exists(PROGRESS_FILE):
        return {
            "solved_problems": [],
            "companies_applied": [],
            "mock_interviews": 0,
            "system_design_sessions": 0,
            "side_project_done": False,
            "resume_updated": False,
            "linkedin_updated": False,
            "notes": [],
        }
    with open(PROGRESS_FILE) as f:
        return json.load(f)


def save(data: dict):
    _ensure_dir()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def save_chat_id(chat_id: int):
    _ensure_dir()
    with open(CHAT_FILE, "w") as f:
        f.write(str(chat_id))


def load_chat_id() -> int | None:
    if not os.path.exists(CHAT_FILE):
        return None
    with open(CHAT_FILE) as f:
        val = f.read().strip()
        return int(val) if val else None


def get_stats() -> dict:
    data = load()
    return {
        "total_solved": len(data["solved_problems"]),
        "solved_problems": data["solved_problems"],
        "companies_applied": len(data["companies_applied"]),
        "companies_list": data["companies_applied"],
        "mock_interviews": data["mock_interviews"],
        "system_design_sessions": data["system_design_sessions"],
        "side_project_done": data["side_project_done"],
        "resume_updated": data["resume_updated"],
        "linkedin_updated": data["linkedin_updated"],
        "notes": data["notes"],
    }


def log_activity(activity_type: str, detail: str = "") -> str:
    data = load()
    today = str(date.today())

    messages = {
        "mock_interview":   "Mock interview logged! Every session sharpens you.",
        "system_design":    "System design session logged! You're building a skill interviewers pay for.",
        "company_applied":  f"Application to *{detail}* logged! Keep building the pipeline.",
        "problem_solved":   f"LC {detail} marked solved! Keep the streak going.",
        "note":             f"Note saved.",
        "resume_done":      "Resume update marked done! Metrics make the difference.",
        "linkedin_done":    "LinkedIn update marked done! Recruiters will start finding you.",
        "project_done":     "Side project marked deployed! Add it to your resume now.",
    }

    if activity_type == "mock_interview":
        data["mock_interviews"] = data.get("mock_interviews", 0) + 1

    elif activity_type == "system_design":
        data["system_design_sessions"] = data.get("system_design_sessions", 0) + 1

    elif activity_type == "company_applied" and detail:
        data.setdefault("companies_applied", []).append({"company": detail, "date": today})

    elif activity_type == "problem_solved" and detail:
        existing_ids = {str(p["id"]) for p in data.get("solved_problems", [])}
        if detail not in existing_ids:
            data.setdefault("solved_problems", []).append({"id": detail, "date": today})
        else:
            return f"LC {detail} was already marked solved."

    elif activity_type == "note" and detail:
        data.setdefault("notes", []).append({"date": today, "text": detail})

    elif activity_type == "resume_done":
        data["resume_updated"] = True

    elif activity_type == "linkedin_done":
        data["linkedin_updated"] = True

    elif activity_type == "project_done":
        data["side_project_done"] = True

    save(data)
    return messages.get(activity_type, "Logged.")


def load_history() -> list[dict]:
    _ensure_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE) as f:
        return json.load(f)


def save_history(history: list[dict]):
    _ensure_dir()
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-40:], f, indent=2)
