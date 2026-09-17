import os
import json
import re
from datetime import date
from config import LEETCODE_DIR, PROGRESS_FILE, BOT_DIR


def ensure_bot_dir():
    os.makedirs(BOT_DIR, exist_ok=True)


def load_progress() -> dict:
    ensure_bot_dir()
    if not os.path.exists(PROGRESS_FILE):
        return {
            "solved_problems": [],
            "companies_applied": [],
            "mock_interviews": 0,
            "system_design_sessions": 0,
            "side_project_done": False,
            "resume_updated": False,
            "linkedin_updated": False,
            "aws_cert_done": False,
            "notes": [],
        }
    with open(PROGRESS_FILE) as f:
        return json.load(f)


def save_progress(data: dict):
    ensure_bot_dir()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def scan_leetcode_dir() -> list[dict]:
    """
    Scans ~/LeetCode for solved problems.
    Each problem folder is named like '88. Merge Sorted Array'.
    Returns list of {id, name, folder} dicts.
    """
    solved = []
    if not os.path.isdir(LEETCODE_DIR):
        return solved

    pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    for entry in os.listdir(LEETCODE_DIR):
        m = pattern.match(entry)
        if m and os.path.isdir(os.path.join(LEETCODE_DIR, entry)):
            solved.append({
                "id": int(m.group(1)),
                "name": m.group(2).strip(),
                "folder": entry,
            })

    solved.sort(key=lambda x: x["id"])
    return solved


def get_stats() -> dict:
    solved_in_dir = scan_leetcode_dir()
    progress = load_progress()

    # Merge: problems tracked in JSON + those found in directory
    dir_ids = {p["id"] for p in solved_in_dir}
    json_ids = {p["id"] for p in progress.get("solved_problems", [])}
    all_solved_ids = dir_ids | json_ids

    companies_list = progress.get("companies_applied", [])
    return {
        "total_solved": len(all_solved_ids),
        "solved_in_dir": solved_in_dir,
        "companies_applied": len(companies_list),
        "companies_list": companies_list,
        "mock_interviews": progress.get("mock_interviews", 0),
        "system_design_sessions": progress.get("system_design_sessions", 0),
        "side_project_done": progress.get("side_project_done", False),
        "resume_updated": progress.get("resume_updated", False),
        "linkedin_updated": progress.get("linkedin_updated", False),
        "notes": progress.get("notes", []),
    }


def log_activity(activity_type: str, detail: str = ""):
    """Log an activity: mock_interview, system_design, company_applied, note."""
    progress = load_progress()
    today = str(date.today())

    if activity_type == "mock_interview":
        progress["mock_interviews"] = progress.get("mock_interviews", 0) + 1

    elif activity_type == "system_design":
        progress["system_design_sessions"] = progress.get("system_design_sessions", 0) + 1

    elif activity_type == "company_applied":
        progress.setdefault("companies_applied", []).append({
            "company": detail,
            "date": today,
        })

    elif activity_type == "note":
        progress.setdefault("notes", []).append({
            "date": today,
            "text": detail,
        })

    elif activity_type == "resume_done":
        progress["resume_updated"] = True

    elif activity_type == "linkedin_done":
        progress["linkedin_updated"] = True

    elif activity_type == "project_done":
        progress["side_project_done"] = True

    save_progress(progress)
    return True
