
import json
import os

from client import MODEL, text_of, client


# --------------------------------------------------
# 1. Workspace setup
# --------------------------------------------------

WORKSPACE = os.path.abspath("workspace")
os.makedirs(WORKSPACE, exist_ok=True)


def safe(path):
    full = os.path.abspath(os.path.join(WORKSPACE, path))

    if not full.startswith(WORKSPACE + os.sep):
        raise ValueError("Path is outside the workspace")

    return full


def read_file(path):
    with open(safe(path), encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(safe(path), "w", encoding="utf-8") as f:
        f.write(content)

    return "wrote " + path


def list_files():
    return ", ".join(os.listdir(WORKSPACE)) or "empty"


# --------------------------------------------------
# 2. Tool definitions
# --------------------------------------------------

TOOLS = [
    {
        "name": "list_files",
        "description": "List files in the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "read_file",
        "description": "Read a text file from the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a text file in the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    }
]


# --------------------------------------------------
# 3. Map tool names to Python functions
# --------------------------------------------------

HANDLERS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file
}


# --------------------------------------------------
# 4. Main agent loop
# --------------------------------------------------

def run_agent(
    goal,
    system,
    tools=TOOLS,
    handlers=HANDLERS,
    max_turns=10,
    max_cost_usd=0.10
):

    messages = [
        {
            "role": "user",
            "content": goal
        }
    ]

    spent = 0.0
    seen = set()

    # Outer loop: controls how many times Claude gets to act
    for turn in range(1, max_turns + 1):

        resp = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=system,
            tools=tools,
            messages=messages
        )

        # Estimate API cost
        spent += (
            resp.usage.input_tokens / 1e6 * 1.0
            + resp.usage.output_tokens / 1e6 * 5.0
        )

        # Save Claude's response in conversation history
        messages.append({
            "role": "assistant",
            "content": resp.content
        })

        # If Claude has finished, return its answer
        if resp.stop_reason != "tool_use":
            return {
                "status": "done",
                "answer": text_of(resp),
                "turns": turn,
                "cost": round(spent, 4)
            }

        # Collect all tool results for this turn
        results = []

        # Inner loop: processes each tool Claude requested
        for b in resp.content:

            if b.type != "tool_use":
                continue

            print(f"Turn {turn}: {b.name}({b.input})")

            key = (b.name, json.dumps(b.input, sort_keys=True))

            if key in seen:
                out, err = (
                    "You already made this exact call. "
                    "Try something different or finish.",
                    True
                )

            else:
                seen.add(key)

                try:
                    out = handlers[b.name](**b.input)
                    err = False

                except Exception as e:
                    out = f"Error: {e}"
                    err = True

            # Construct result for this particular tool call
            item = {
                "type": "tool_result",
                "tool_use_id": b.id,
                "content": str(out)[:4000]
            }

            if err:
                item["is_error"] = True

            results.append(item)

        # Important: outside inner loop, inside outer loop
        # Send all tool results back to Claude together
        messages.append({
            "role": "user",
            "content": results
        })

        # Check spending limit
        if spent > max_cost_usd:
            return {
                "status": "over_budget",
                "turns": turn,
                "cost": round(spent, 4)
            }

    return {
        "status": "max_turns",
        "turns": max_turns,
        "cost": round(spent, 4)
    }