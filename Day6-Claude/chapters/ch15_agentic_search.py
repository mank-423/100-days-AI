
from pathlib import Path

from client import text_of
from chapters.ch13_rag import Library
from toolkit import run_with_tools


# --------------------------------------------------
# 1. Load the book and create the BM25 library
# --------------------------------------------------

path = Path(__file__).parent / "book.txt"
lib = Library(path.read_text(encoding="utf-8"))


# --------------------------------------------------
# 2. Define tool functions
# --------------------------------------------------

def search_notes(query):
    """Search the book and return short previews with chunk IDs."""
    return "\n".join(
        f"[{i}] {c[:150]}..."
        for i, c in lib.search(query, k=4)
    )


def read_chunk(chunk_id):
    """Read the full text of a chunk using its ID."""
    chunk_id = int(chunk_id)

    if not 0 <= chunk_id < len(lib.chunks):
        return f"Invalid chunk ID: {chunk_id}"

    return lib.chunks[chunk_id]


# --------------------------------------------------
# 3. Expose tools to Claude
# --------------------------------------------------

tools = [
    {
        "name": "search_notes",
        "description": (
            "Keyword search over the book. "
            "Returns short previews with IDs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_chunk",
        "description": (
            "Read the full text of one chunk by ID, "
            "after searching."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "chunk_id": {"type": "integer"}
            },
            "required": ["chunk_id"],
        },
    },
]


# --------------------------------------------------
# 4. System instructions
# --------------------------------------------------

system = """
Search before answering.

You may search several times.
Read the full chunks that are relevant.
Compare the information carefully.
Cite chunk IDs like [3].

If you cannot find the answer in the book, say so.
"""


# --------------------------------------------------
# 5. Run the agent
# --------------------------------------------------

if __name__ == "__main__":

    msgs = [
        {
            "role": "user",
            "content": (
                "Compare how the book describes "
                "osmosis and diffusion."
            ),
        }
    ]

    final = run_with_tools(
        msgs,
        tools,
        {
            "search_notes": search_notes,
            "read_chunk": read_chunk,
        },
        system=system,
        max_turns=6,
    )

    print("\n--- FINAL ANSWER ---\n")
    print(text_of(final))
