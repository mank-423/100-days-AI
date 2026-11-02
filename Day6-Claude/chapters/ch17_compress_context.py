
from client import client, MODEL, text_of


# --------------------------------------------------
# 1. Convert conversation messages into readable text
# --------------------------------------------------

def render(messages):
    lines = []

    for m in messages:
        content = m["content"]
        role = m["role"]

        if isinstance(content, str):
            lines.append(role + ": " + content)
            continue

        for b in content:
            block_type = (
                b.get("type") if isinstance(b, dict)
                else getattr(b, "type", None)
            )

            def get_value(key, default=None):
                if isinstance(b, dict):
                    return b.get(key, default)
                return getattr(b, key, default)

            if block_type == "tool_result":
                result = get_value("content", "")
                if isinstance(result, list):
                    result = " ".join(
                        getattr(x, "text", str(x))
                        for x in result
                    )

                lines.append("tool result: " + str(result)[:300])

            elif block_type == "tool_use":
                name = get_value("name", "unknown")
                tool_input = get_value("input", {})
                lines.append(
                    f"{role}: called tool {name} with {tool_input}"
                )

            elif get_value("text"):
                lines.append(role + ": " + get_value("text"))

    return "\n".join(lines)


# --------------------------------------------------
# 2. Find a safe point to split the conversation
# --------------------------------------------------

def split_point(messages, keep_last=4):

    # Search backwards for a plain user message.
    # This avoids splitting tool calls from their results.

    for i in range(len(messages) - keep_last, 0, -1):

        if (
            messages[i]["role"] == "user"
            and isinstance(messages[i]["content"], str)
        ):
            return i

    return 0


# --------------------------------------------------
# 3. Compact older conversation history
# --------------------------------------------------

def compact(messages, keep_last=4):

    i = split_point(messages, keep_last)

    if i <= 0:
        return messages

    old = messages[:i]
    recent = messages[i:]

    r = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarize this conversation so work can continue. "
                    "Keep goals, decisions, key facts, files touched "
                    "and open tasks. Be brief.\n\n"
                    + render(old)
                ),
            }
        ],
    )

    summary = text_of(r)

    head = [
        {
            "role": "user",
            "content": (
                "<summary of earlier conversation>\n"
                + summary
                + "\n</summary>"
            ),
        },
        {
            "role": "assistant",
            "content": "Understood. Continuing from the summary.",
        },
    ]

    return head + recent


# --------------------------------------------------
# 4. Check token count and compact when necessary
# --------------------------------------------------

def maybe_compact(messages, limit_tokens=20000):

    n = client.messages.count_tokens(
        model=MODEL,
        messages=messages,
    ).input_tokens

    print(f"Current input tokens: {n}")

    if n > limit_tokens:
        print("Context limit reached. Compacting conversation...")
        return compact(messages)

    print("Context is within the limit.")
    return messages

if __name__ == "__main__":

    messages = [
        {"role": "user", "content": "What is RAG?"},
        {"role": "assistant", "content": "RAG stands for Retrieval-Augmented Generation."},
        {"role": "user", "content": "Explain BM25."},
        {"role": "assistant", "content": "BM25 is a lexical search ranking algorithm."},
        {"role": "user", "content": "What is contextual retrieval?"},
        {"role": "assistant", "content": "It adds context to chunks before retrieval."},
    ]

    messages = maybe_compact(messages, limit_tokens=50)

    print("\nFinal conversation:")
    for message in messages:
        print(f"\n{message['role']}: {message['content']}")