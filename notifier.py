import subprocess
import sys


def notify(title: str, message: str, sound: str = "Glass"):
    """Send a macOS desktop notification."""
    script = f'display notification "{message}" with title "{title}" sound name "{sound}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
    except Exception:
        pass  # Notification failed silently — terminal output is the fallback


def print_banner(text: str, char: str = "="):
    width = min(len(text) + 4, 70)
    border = char * width
    print(f"\n{border}")
    print(f"  {text}")
    print(f"{border}\n")


def print_section(title: str):
    print(f"\n--- {title} ---")


def morning_reminder(week_plan: dict, stats: dict):
    solved = stats["total_solved"]
    theme = week_plan["theme"]
    problems = week_plan.get("problems_this_week", [])

    # Desktop notification
    notify(
        "CareerBot — Morning DSA",
        f"Week {week_plan['week']}: {theme}. {solved} problems solved so far. Open LeetCode now!"
    )

    # Terminal output
    print_banner(f"Good morning, Raghav! Time for DSA (6:00 – 7:30 AM)")

    print(f"This week's theme: {theme}")
    print(f"Problems solved so far: {solved} / 100+ target\n")

    if problems:
        unsolved_next = [p for p in problems if p["id"] not in {s["id"] for s in stats["solved_in_dir"]}]
        if unsolved_next:
            next_p = unsolved_next[0]
            print(f"Solve next: LC {next_p['id']}. {next_p['name']} ({next_p['diff']})")
            print(f"Hint: {next_p['hint']}\n")
        else:
            print("You've finished this week's problems! Start next week's list or revisit hard ones.\n")
    else:
        print("This week: Mock interview / revision mode. Open Pramp and start a session.\n")

    print("Remember: Understand the pattern. Explain your thinking out loud.")


def evening_reminder(week_plan: dict, stats: dict):
    task = week_plan.get("evening_task", "Study system design or work on applications")

    notify(
        "CareerBot — Evening Study",
        f"8 PM: {task}"
    )

    print_banner("Evening Study Block (8:00 – 9:30 PM)")
    print(f"Tonight's focus: {task}\n")

    if not stats["resume_updated"]:
        print("ACTION: Resume still not updated with metrics! Do this tonight.")
    if not stats["linkedin_updated"]:
        print("ACTION: LinkedIn not updated yet. 10 minutes — do it now.")
    if stats["companies_applied"] < 5 and week_plan["week"] >= 4:
        print(f"ACTION: Only {stats['companies_applied']} applications sent. Target is 15-20 by end of Month 2.")


def weekly_reminder(week_plan: dict, stats: dict):
    notify(
        "CareerBot — Weekly Review",
        f"Sunday review time! Week {week_plan['week']} wrap-up. Open Notion."
    )

    print_banner(f"Sunday Weekly Review — Week {week_plan['week']}")
    print(f"Problems solved total: {stats['total_solved']}")
    print(f"Companies applied: {stats['companies_applied']}")
    print(f"Mock interviews done: {stats['mock_interviews']}")
    print(f"System design sessions: {stats['system_design_sessions']}")
    print()

    if stats["total_solved"] < week_plan["week"] * 5:
        expected = week_plan["week"] * 5
        print(f"WARNING: You're behind. Expected ~{expected} problems solved by now.")
        print("Double down on mornings this week. Skip no day.\n")
    else:
        print("On track! Keep the momentum going.\n")

    print("Open your Notion Weekly Review Log and fill in this week's entry.")
    print("Set your 3 priorities for next week before you close Notion.")
