
import json
import os
import time

from chapters.harness import init, run_session, load_tasks
from toolkit import cost_usd


MAX_SESSIONS = 12
MAX_COST_USD = 0.50

KILL_SWITCH = "state/STOP"


def event(e):
    with open("state/loop.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(e) + "\n")


def run_loop():
    if not os.path.exists("state/tasks.json"):
        init(
            sorted(
                f for f in os.listdir("chapters")
                if f.endswith(".txt")
            )
        )

    last_fail, repeats = None, 0

    for n in range(1, MAX_SESSIONS + 1):

        # 1. Check manual stop switch.
        if os.path.exists(KILL_SWITCH):
            return "stopped: kill switch"

        # 2. Execute one worker session.
        status = run_session()

        # 3. Get cumulative cost.
        spent = cost_usd()

        # 4. Record the event.
        event({
            "n": n,
            "status": status,
            "cost": round(spent, 4),
            "time": time.time(),
        })

        print(n, status, f"${spent:.3f}")

        # 5. Check whether all tasks are complete.
        if status == "idle":
            left = [
                t["id"]
                for t in load_tasks()
                if not t["passes"]
            ]

            return (
                "finished"
                if not left
                else "needs a human, still failing: " + ", ".join(left)
            )

        # 6. Check spending limit.
        if spent >= MAX_COST_USD:
            return "stopped: budget reached"

        # 7. Detect repeated failures.
        if status.startswith("fail:"):
            repeats = repeats + 1 if status == last_fail else 1
            last_fail = status

            if repeats >= 3:
                return "stopped: stuck on " + status

        else:
            last_fail, repeats = None, 0

    return "stopped: session limit"


if __name__ == "__main__":
    print(run_loop())
