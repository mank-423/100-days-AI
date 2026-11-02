
from pathlib import Path
from chapters.ch13_rag import Library


# --------------------------------------------------
# 1. Load course notes
# --------------------------------------------------

book_path = Path(__file__).parent / "book.txt"
book = book_path.read_text(encoding="utf-8")

lib = Library(book)


# --------------------------------------------------
# 2. Define the tool schema
# --------------------------------------------------

good = {
    "name": "search_notes",
    "description": (
        "Keyword search over the student course notes. "
        "Use for questions about course content. "
        "Returns previews with ids; call read_chunk for full text. "
        "Not for current events."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "two to five keywords, not a full sentence"
            },
            "limit": {
                "type": "integer",
                "description": "max results, default 4, max 8"
            },
            "detail": {
                "type": "string",
                "enum": ["concise", "detailed"],
                "description": "concise = 150 chars per hit"
            }
        },
        "required": ["query"]
    }
}


# --------------------------------------------------
# 3. Define the Python handler
# --------------------------------------------------

def search_handler(lib, query, limit=4, detail="concise"):

    # Keep the limit between 1 and 8
    limit = max(1, min(limit, 8))

    hits = lib.search(query, k=limit)

    if not hits:
        return "No results. Try fewer or different keywords."

    width = 150 if detail == "concise" else 600

    out = "\n".join(
        f"[{i}] {c[:width]}"
        for i, c in hits
    )

    return out[:3000]


# --------------------------------------------------
# 4. Test the handler directly
# --------------------------------------------------

if __name__ == "__main__":

    print("Concise search:\n")

    result = search_handler(
        lib,
        query="BM25 retrieval",
        limit=4,
        detail="concise"
    )

    print(result)

    print("\n" + "=" * 50)

    print("Detailed search:\n")

    result = search_handler(
        lib,
        query="BM25 retrieval",
        limit=4,
        detail="detailed"
    )

    print(result)
