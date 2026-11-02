
"""
Contextual Retrieval using:
1. Claude to contextualize document chunks
2. BM25 for lexical retrieval
3. Claude to rerank retrieved chunks
4. Claude to generate the final answer
"""

import re
from pathlib import Path

from rank_bm25 import BM25Okapi
from client import client, MODEL, text_of
from .ch13_rag import chunk, tok


# --------------------------------------------------
# 1. Contextualize each chunk
# --------------------------------------------------

def contextualize(doc, piece):
    r = client.messages.create(
        model=MODEL,
        max_tokens=120,
        system=[
            {
                "type": "text",
                "text": f"<document>\n{doc}\n</document>",
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"<chunk>\n{piece}\n</chunk>\n"
                    "Write a short context (1 to 2 sentences) "
                    "that situates this chunk within the whole "
                    "document, to improve search. "
                    "Answer with the context only."
                ),
            }
        ],
    )

    return text_of(r)


# --------------------------------------------------
# 2. Build the contextual BM25 library
# --------------------------------------------------

class ContextLibrary:

    def __init__(self, doc, max_chunks=20):
        self.chunks = chunk(doc)[:max_chunks]

        print(f"Contextualizing {len(self.chunks)} chunks...")

        self.ctx = [
            contextualize(doc, piece)
            for piece in self.chunks
        ]

        self.bm25 = BM25Okapi([
            tok(context + " " + piece)
            for context, piece in zip(self.ctx, self.chunks)
        ])

        print("Context library ready!")

    def search(self, query, k=10):
        scores = self.bm25.get_scores(tok(query))

        top = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]

        return [
            (i, self.ctx[i] + "\n" + self.chunks[i])
            for i in top
        ]


# --------------------------------------------------
# 3. Rerank retrieved chunks using Claude
# --------------------------------------------------

def rerank(question, hits, keep=3):

    listing = "\n\n".join(
        f"[{i}]\n{content[:500]}"
        for i, content in hits
    )

    r = client.messages.create(
        model=MODEL,
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Passages:\n{listing}\n\n"
                    f"Select the {keep} most relevant passages "
                    "for answering the question.\n"
                    "Return only their IDs as comma-separated numbers."
                ),
            }
        ],
    )

    # Extract and validate IDs returned by Claude
    candidate_ids = {i for i, _ in hits}

    ids = []
    for x in re.findall(r"\d+", text_of(r)):
        i = int(x)

        if i in candidate_ids and i not in ids:
            ids.append(i)

        if len(ids) == keep:
            break

    return [
        (i, content)
        for i, content in hits
        if i in ids
    ]


# --------------------------------------------------
# 4. Generate the final answer
# --------------------------------------------------

def answer_question(question, hits):

    sources = "\n\n".join(
        f'<source id="{i}">\n{content}\n</source>'
        for i, content in hits
    )

    prompt = f"""
Use the following retrieved sources to answer the question.

{sources}

Question: {question}

Instructions:
- Answer using only the provided sources.
- Cite source IDs like [3].
- If the sources do not contain the answer, say you do not know.
"""

    r = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return text_of(r)


# --------------------------------------------------
# 5. Main execution
# --------------------------------------------------

if __name__ == "__main__":

    path = Path(__file__).parent / "book.txt"
    doc = path.read_text(encoding="utf-8")

    question = "What does the book say about cell membranes?"

    # Build the library
    lib = ContextLibrary(doc)

    # Retrieve candidates using BM25
    print("\nSearching with BM25...")
    hits = lib.search(question, k=10)

    print(f"\nRetrieved {len(hits)} chunks.")

    # Rerank candidates using Claude
    print("\nReranking with Claude...")
    best_hits = rerank(question, hits, keep=3)

    print(f"Selected {len(best_hits)} chunks.")

    # Generate final answer
    print("\nGenerating final answer...\n")
    result = answer_question(question, best_hits)

    print("=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(result)
