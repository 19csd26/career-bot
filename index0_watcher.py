#!/usr/bin/env python3
"""
Index 0 → LeetCode Bridge
Polls Index 0's SQLite DB every 10s for newly completed sessions.
When a problem is completed, writes the code + markdown into ~/LeetCode/<folder>/
so lc_watcher.py picks it up and auto-commits to GitHub.
"""

import json
import re
import sqlite3
import time
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

INDEX0_DB    = Path.home() / "Library/Application Support/index_0/data/sessions.db"
LEETCODE_DIR = Path.home() / "LeetCode"
DATA_DIR     = Path(__file__).parent / "data"
PROCESSED    = DATA_DIR / "index0_processed.json"
LC_CACHE     = DATA_DIR / "lc_problem_cache.json"

POLL_SECS = 10

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("index0-watcher")

LANG_EXT = {
    "java":       ".java",
    "python":     ".py",
    "python3":    ".py",
    "javascript": ".js",
    "typescript": ".ts",
    "ruby":       ".rb",
    "go":         ".go",
    "cpp":        ".cpp",
    "c":          ".c",
    "rust":       ".rs",
    "kotlin":     ".kt",
    "swift":      ".swift",
}


# ── Persistence ────────────────────────────────────────────────────────────────

def load_processed() -> dict:
    """Returns {slug: session_id} for already-written problems."""
    if PROCESSED.exists():
        data = json.loads(PROCESSED.read_text())
        # migrate old list format → dict
        if isinstance(data, list):
            return {}
        return data
    return {}

def save_processed(done: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED.write_text(json.dumps(done, indent=2))

def load_lc_cache() -> dict:
    if LC_CACHE.exists():
        return json.loads(LC_CACHE.read_text())
    return {}

def save_lc_cache(cache: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LC_CACHE.write_text(json.dumps(cache, indent=2))


# ── LeetCode API ───────────────────────────────────────────────────────────────

def fetch_lc_problem(slug: str) -> dict | None:
    cache = load_lc_cache()
    if slug in cache:
        return cache[slug]

    try:
        r = requests.post(
            "https://leetcode.com/graphql",
            json={
                "query": """
                    query($slug: String!) {
                        question(titleSlug: $slug) {
                            questionId
                            title
                            difficulty
                        }
                    }
                """,
                "variables": {"slug": slug},
            },
            headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
            timeout=10,
        )
        q = r.json().get("data", {}).get("question")
        if not q:
            return None

        result = {"id": q["questionId"], "title": q["title"], "difficulty": q["difficulty"]}
        cache[slug] = result
        save_lc_cache(cache)
        return result

    except Exception as e:
        log.warning(f"LeetCode API failed for '{slug}': {e}")
        return None


# ── Index 0 DB ─────────────────────────────────────────────────────────────────

def completed_sessions(conn) -> list[dict]:
    rows = conn.execute("""
        SELECT id, problem_id, created_at
        FROM sessions
        WHERE stage = 'final' AND status = 'completed'
        ORDER BY created_at DESC
    """).fetchall()
    return [{"id": r[0], "slug": r[1], "completed_at": r[2]} for r in rows]


def best_passing_run(conn, session_id: str, slug: str) -> dict | None:
    row = conn.execute("""
        SELECT code, language, passed_count, total_count, runtime_ms
        FROM runs
        WHERE session_id = ? AND problem_id = ? AND passed = 1 AND code IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
    """, (session_id, slug)).fetchone()

    if row and row[0] and row[0].strip():
        return {"code": row[0], "language": row[1],
                "passed_count": row[2], "total_count": row[3], "runtime_ms": row[4]}
    return None


def coach_insights(conn, session_id: str) -> list[str]:
    skip = {"let's start with the problem", "in your own words", "where were we"}
    rows = conn.execute("""
        SELECT content FROM messages
        WHERE session_id = ? AND role = 'coach'
        ORDER BY created_at
    """, (session_id,)).fetchall()
    out = []
    for (text,) in rows:
        if text and not any(p in text.lower() for p in skip):
            out.append(text.strip())
    return out[:4]


# ── File generation ────────────────────────────────────────────────────────────

def code_filename(slug: str, lang: str) -> str:
    ext = LANG_EXT.get(lang, f".{lang}")
    if ext in (".java", ".kt", ".swift"):
        return "".join(w.capitalize() for w in slug.split("-")) + ext
    return slug.replace("-", "_") + ext


def generate_md(slug: str, lc: dict, run: dict, insights: list[str]) -> str:
    title   = lc["title"]
    lc_id   = lc["id"]
    diff    = lc["difficulty"]
    lang    = run["language"].capitalize()
    passed  = run.get("passed_count", "?")
    total   = run.get("total_count", "?")
    ms      = run.get("runtime_ms", "?")
    cf      = code_filename(slug, run["language"])
    date    = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    coach_block = ""
    if insights:
        lines = "\n\n".join(f"> {i}" for i in insights)
        coach_block = f"\n## Coach Notes (from Index 0 session)\n\n{lines}\n"

    return f"""# {title} (LeetCode {lc_id})

**Difficulty:** {diff} · **Language:** {lang} · **Tests:** {passed}/{total} · **Runtime:** {ms}ms

---

## Solution

See [`{cf}`](./{cf}) for the full solution.

## Complexity

| | |
|---|---|
| **Time**  | O(n) |
| **Space** | O(1) |
{coach_block}
---

*Auto-documented from Index 0 — {date}*
"""


# ── Bridge ─────────────────────────────────────────────────────────────────────

def process_session(conn, session: dict, processed: dict):
    slug = session["slug"]
    sid  = session["id"]

    lc = fetch_lc_problem(slug)
    if not lc:
        log.warning(f"Could not resolve LC number for '{slug}' — will retry next poll.")
        return

    # Use the best passing run across ALL sessions for this slug
    row = conn.execute("""
        SELECT code, language, passed_count, total_count, runtime_ms
        FROM runs
        WHERE problem_id = ? AND passed = 1 AND code IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
    """, (slug,)).fetchone()

    if not row or not row[0] or not row[0].strip():
        log.warning(f"No passing code found for '{slug}' — skipping.")
        return

    run = {"code": row[0], "language": row[1],
           "passed_count": row[2], "total_count": row[3], "runtime_ms": row[4]}

    # Get insights from the most recently completed session
    latest_sid = conn.execute("""
        SELECT id FROM sessions
        WHERE problem_id = ? AND stage = 'final' AND status = 'completed'
        ORDER BY created_at DESC LIMIT 1
    """, (slug,)).fetchone()[0]

    folder_name = f"{lc['id']}. {lc['title']}"
    folder      = LEETCODE_DIR / folder_name
    folder.mkdir(parents=True, exist_ok=True)

    cf = code_filename(slug, run["language"])
    (folder / cf).write_text(run["code"])
    (folder / f"{slug}.md").write_text(generate_md(slug, lc, run, coach_insights(conn, latest_sid)))

    log.info(f"Written: ~/LeetCode/{folder_name}/")
    log.info(f"  {cf}  |  {run['passed_count']}/{run['total_count']} tests  |  {run['runtime_ms']}ms  |  {run['language']}")
    log.info(f"  lc_watcher will auto-commit in ~12s")

    processed[slug] = sid
    save_processed(processed)


def poll():
    LEETCODE_DIR.mkdir(exist_ok=True)
    processed = load_processed()

    log.info("Index 0 → LeetCode bridge running")
    log.info(f"DB:     {INDEX0_DB}")
    log.info(f"Output: {LEETCODE_DIR}")
    log.info(f"Polling every {POLL_SECS}s\n")

    while True:
        try:
            conn = sqlite3.connect(f"file:{INDEX0_DB}?mode=ro", uri=True)

            # completed_sessions returns DESC — first occurrence per slug is the newest
            latest: dict[str, dict] = {}
            for s in completed_sessions(conn):
                if s["slug"] not in latest:
                    latest[s["slug"]] = s

            for slug, s in latest.items():
                if slug not in processed or processed[slug] != s["id"]:
                    log.info(f"New completion detected: {slug}")
                    process_session(conn, s, processed)

            conn.close()
        except Exception as e:
            log.error(f"Poll error: {e}")

        time.sleep(POLL_SECS)


if __name__ == "__main__":
    if not INDEX0_DB.exists():
        log.error(f"Index 0 DB not found: {INDEX0_DB}")
        log.error("Open Index 0 at least once, then retry.")
        exit(1)
    poll()
