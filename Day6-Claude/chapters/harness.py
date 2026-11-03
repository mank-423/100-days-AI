
import json
import os

from client import text_of
from toolkit import run_with_tools

STATE = "state"
OUT = "out"

os.makedirs(STATE, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

TASKS = os.path.join(STATE, "tasks.json")
PROGRESS = os.path.join(STATE, "progress.md")


def load_tasks():
    with open(TASKS, encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(TASKS, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def log(*parts):
    with open(PROGRESS, "a", encoding="utf-8") as f:
        f.write(" | ".join(parts) + "\n")


def init(chapter_files):
    # The initializer: runs once and creates the task plan.
    tasks = [
        {
            "id": f"{name}-{kind}",
            "chapter": name,
            "kind": kind,
            "passes": False,
            "attempts": 0,
        }
        for name in chapter_files
        for kind in ("summary", "flashcards")
    ]

    save_tasks(tasks)
    log("init", f"{len(tasks)} tasks created")


def save_output(filename, content):
    # Only save the basename, preventing directory traversal.
    safe_filename = os.path.basename(filename)

    path = os.path.join(OUT, safe_filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return "saved " + safe_filename


SAVE_TOOL = [
    {
        "name": "save_output",
        "description": "Save the finished output file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["filename", "content"],
        },
    }
]


def verify(task):
    # Verify the actual artifact, not the model's claim.
    ext = ".md" if task["kind"] == "summary" else ".json"

    path = os.path.join(OUT, task["id"] + ext)

    if not os.path.exists(path):
        return False, "output file missing"

    if task["kind"] == "summary":
        with open(path, encoding="utf-8") as f:
            n = sum(
                1 for line in f
                if line.strip().startswith("-")
            )

        return n >= 3, f"{n} bullets"

    try:
        with open(path, encoding="utf-8") as f:
            cards = json.load(f)
    except Exception as e:
        return False, f"invalid json: {e}"

    valid = (
        isinstance(cards, list)
        and len(cards) >= 5
        and all(
            isinstance(card, dict)
            and "question" in card
            and "answer" in card
            for card in cards
        )
    )

    return valid, f"{len(cards) if isinstance(cards, list) else 0} cards"


def run_session():
    tasks = load_tasks()

    # Pick the first unfinished task with fewer than 3 attempts.
    task = next(
        (
            t for t in tasks
            if not t["passes"] and t["attempts"] < 3
        ),
        None,
    )

    if task is None:
        return "idle"

    tid = task["id"]
    kind = task["kind"]

    tail = ""
    if os.path.exists(PROGRESS):
        with open(PROGRESS, encoding="utf-8") as f:
            tail = f.read()[-1500:]

    chapter_path = os.path.join("chapters", task["chapter"])

    with open(chapter_path, encoding="utf-8") as f:
        chapter_text = f.read()[:6000]

    if kind == "summary":
        spec = (
            f"file name {tid}.md: 3 to 5 bullet lines, "
            "each starting with a dash"
        )
    else:
        spec = (
            f"file name {tid}.json: a JSON list of at least "
            "5 objects with question and answer keys"
        )

    goal = (
        f"<progress_log>\n{tail}\n</progress_log>\n"
        f"<chapter>\n{chapter_text}\n</chapter>\n"
        f"Task {tid}: create {spec}. "
        "Save it with save_output."
    )

    system = (
        "You are one worker session in a harness. "
        "Do only this one task. "
        "The harness verifies your file, so do not claim success."
    )

    task["attempts"] += 1

    try:
        run_with_tools(
            [{"role": "user", "content": goal}],
            SAVE_TOOL,
            {"save_output": save_output},
            system=system,
            max_turns=4,
            max_tokens=1500,
        )
    except RuntimeError as e:
        log(tid, "error", str(e))

    ok, note = verify(task)

    task["passes"] = ok

    save_tasks(tasks)

    log(
        tid,
        "PASS" if ok else "FAIL",
        note,
        f"attempt {task['attempts']}",
    )

    return ("pass:" if ok else "fail:") + tid
