
import os

from chapters.harness import init, run_session


if not os.path.exists("state/tasks.json"):
    init(
        sorted(
            f for f in os.listdir("chapters")
            if f.endswith(".txt")
        )
    )

print(run_session())
