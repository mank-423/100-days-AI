"""
BM25 scores documents based on things like:
- Term frequency (TF): How often do the query's words appear in the document?
- Inverse document frequency (IDF): How rare and informative are those words across the whole collection?
- Document length: Is the document unusually long, making word matches less meaningful?
"""

import re
from rank_bm25 import BM25Okapi
from pathlib import Path
from client import client, MODEL, text_of


def chunk(text, size=800, overlap=150):
    out, i = [], 0

    while i < len(text):
        out.append(text[i : i + size])
        i += size - overlap

    return out


def tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())


class Library:
    def __init__(self, text):
        self.chunks = chunk(text)
        self.bm25 = BM25Okapi([tok(c) for c in self.chunks])

    def search(self, query, k=4):
        scores = self.bm25.get_scores(tok(query))

        top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

        return [(i, self.chunks[i]) for i in top]

    def answer(self, question):
        hits = self.search(question)

        sources = "\n\n".join(f'<source id="{i}">{c}</source>' for i, c in hits)

        prompt = f"""
{sources}

Question: {question}

Answer using only the sources. Cite source IDs like [3].
If the sources do not contain the answer, say you do not know.
"""

        r = client.messages.create(
            model=MODEL, max_tokens=400, messages=[{"role": "user", "content": prompt}]
        )

        return text_of(r)


if __name__ == "__main__":
    path = Path(__file__).parent / "book.txt"

    with open(path, encoding="utf-8") as f:
        lib = Library(f.read())

    print(lib.answer("What does the book say about cell membranes?"))
