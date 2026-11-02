
from pathlib import Path

from client import client, MODEL, text_of
from chapters.ch13_rag import Library


# --------------------------------------------------
# 1. Load the book and create the BM25 library
# --------------------------------------------------

path = Path(__file__).parent / "book.txt"
book = path.read_text(encoding="utf-8")

lib = Library(book)


# --------------------------------------------------
# 2. Prepare the question and retrieve relevant chunks
# --------------------------------------------------

q = "What is osmosis?"

focused = "\n\n".join(
    c for _, c in lib.search(q, k=3)
)


# --------------------------------------------------
# 3. Ask Claude using different context sizes
# --------------------------------------------------

def ask_with(material):

    r = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": (
                    f"<material>\n{material}\n</material>\n\n"
                    f"{q} Answer in 2 sentences."
                ),
            }
        ],
    )

    return text_of(r), r.usage.input_tokens


# Compare full book vs focused chunks
if __name__ == "__main__":

    for name, material in [
        ("Everything", book),
        ("3 focused chunks", focused),
    ]:

        answer, tokens = ask_with(material)

        print(f"\n{name}: {tokens} input tokens")
        print(answer)
        print("-" * 40)


# --------------------------------------------------
# 4. Audit system prompt and tool-definition costs
# --------------------------------------------------

def audit(system, tools, messages):

    total = client.messages.count_tokens(
        model=MODEL,
        system=system,
        tools=tools,
        messages=messages,
    ).input_tokens

    no_tools = client.messages.count_tokens(
        model=MODEL,
        system=system,
        messages=messages,
    ).input_tokens

    print(
        "Total:", total,
        "| Tool definitions cost about:", total - no_tools
    )
