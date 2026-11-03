
from chapters.ch13_rag import Library
from pathlib import Path
from agents.ch26_multiagent import evaluate

BOOK = Path(__file__).resolve().parent.parent / "chapters" / "book.txt"
lib = Library(BOOK.read_text(encoding="utf-8"))

CASES = [
    {
        "q": "What does the book say about cell membranes?",
        "rubric": "States that membranes control what enters and leaves the cell.",
    },
    {
        "q": "Who won the 1998 football World Cup?",
        "rubric": "Admits the book does not contain this information and does not guess.",
    },
]


def run_evals(k):
    passed = 0

    for case in CASES:
        # Retrieve context using the selected k
        hits = lib.search(case["q"], k=k)
        context = "\n\n".join(chunk for _, chunk in hits)

        # Generate answer using retrieved context
        # Adjust this prompt to match your existing RAG answer prompt.
        from client import client, MODEL
        from client import text_of

        response = client.messages.create(
            model=MODEL,
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    "Answer using only the following material. "
                    "If the answer is absent, say you don't know.\n\n"
                    f"<material>\n{context}\n</material>\n\n"
                    f"Question: {case['q']}"
                )
            }]
        )

        answer = text_of(response)

        verdict = evaluate(
            case["q"],
            answer,
            case["rubric"]
        )

        passed += verdict["passed"]

        print(
            f"  {'PASS' if verdict['passed'] else 'FAIL'}"
            f" | {case['q']}"
        )

    return passed


if __name__ == "__main__":
    results = {}

    for k in [2, 4]:
        print(f"\n========== EXPERIMENT: k={k} ==========")
        results[k] = run_evals(k)

    print("\n========== COMPARISON ==========")

    for k, passed in results.items():
        total = len(CASES)
        print(f"k={k}: {passed}/{total} passed ({passed / total * 100:.1f}%)")
