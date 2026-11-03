
from client import client, MODEL, text_of
from toolkit import run_with_tools

from .agent import TOOLS, HANDLERS


# Give sub-agents read-only access.
READ_TOOLS = [
    t for t in TOOLS
    if t["name"] in ("list_files", "read_file")
]

READ_HANDLERS = {
    k: v for k, v in HANDLERS.items()
    if k in ("list_files", "read_file")
}


def sub_agent(task):
    # Each sub-agent gets a fresh conversation.
    print(f"\n[SUB-AGENT STARTED] {task}")

    msgs = [
        {"role": "user", "content": task}
    ]

    final = run_with_tools(
        msgs,
        READ_TOOLS,
        READ_HANDLERS,
        system=(
            "You are a research sub-agent. "
            "Read the relevant workspace files and "
            "reply with a report of at most 120 words."
        ),
        max_turns=5,
        max_tokens=600,
    )

    report = text_of(final)

    print(f"[SUB-AGENT REPORT]\n{report}")

    return report


# Main agent's delegation tool.
DELEGATE = [
    {
        "name": "delegate",
        "description": (
            "Give one independent subtask to a sub-agent "
            "that can read workspace files. "
            "Returns a short report."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string"}
            },
            "required": ["task"],
        },
    }
]


def orchestrate(goal):
    print("\n[ORCHESTRATOR STARTED]")
    print(f"Goal: {goal}")

    msgs = [
        {"role": "user", "content": goal}
    ]

    final = run_with_tools(
        msgs,
        DELEGATE,
        {"delegate": sub_agent},
        system=(
            "You are a research orchestrator. "
            "Split the goal into independent sub-tasks. "
            "Delegate each sub-task to a sub-agent. "
            "Wait for their reports and write a final "
            "answer based on those reports."
        ),
        max_turns=6,
        max_tokens=800,
    )

    return text_of(final)


# Evaluation tool.
GRADE = [
    {
        "name": "grade",
        "description": "Grade the work against the rubric.",
        "input_schema": {
            "type": "object",
            "properties": {
                "passed": {"type": "boolean"},
                "feedback": {"type": "string"},
            },
            "required": ["passed", "feedback"],
        },
    }
]


def evaluate(task, work, rubric):
    r = client.messages.create(
        model=MODEL,
        max_tokens=300,
        tools=GRADE,
        tool_choice={
            "type": "tool",
            "name": "grade",
        },
        system=(
            "You are a strict grader. "
            "Judge only against the rubric. "
            "Do not be generous."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Task: {task}\n"
                    f"Rubric: {rubric}\n"
                    f"Work:\n{work}"
                ),
            }
        ],
    )

    return next(
        b.input for b in r.content
        if b.type == "tool_use"
    )


if __name__ == "__main__":
    result = orchestrate(
        "Compare what each file says about meiosis. "
        "Cover the basic definition, stages, and biological "
        "significance. Identify similarities and differences. "
        "Use all three files and do not invent facts."
    )

    print("\n========== FINAL REPORT ==========")
    print(result)

    rubric = (
        "The answer must accurately cover the definition, "
        "the two meiotic divisions, crossing over, independent "
        "assortment, and biological significance. "
        "It must distinguish meiosis I from meiosis II."
    )

    grade = evaluate(
        "Explain and compare the three meiosis documents.",
        result,
        rubric,
    )

    print("\n========== EVALUATION ==========")
    print(grade)
