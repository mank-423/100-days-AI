
from concurrent.futures import ThreadPoolExecutor
from client import client, MODEL, text_of


def ask(prompt, system=None, max_tokens=500):
    kw = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }

    if system:
        kw["system"] = system

    response = client.messages.create(**kw)
    return text_of(response)


# 1. Prompt chaining: each step feeds into the next
def chain(topic):
    outline = ask(f"Write a 3-point outline about {topic}")

    return ask(
        f"Write a short lesson following this outline:\n{outline}"
    )


# 2. Routing: classify first, then use the right specialist
SPECIALISTS = {
    "definition": "Give a one-sentence definition.",
    "quiz": "Write one multiple-choice question with the answer.",
    "summary": "Summarize in 3 bullet points.",
}


def route(request):
    label = ask(
        f"Classify this request as definition, quiz or summary. "
        f"Reply with one word.\n{request}",
        max_tokens=5
    ).strip().lower()

    system_prompt = SPECIALISTS.get(label, SPECIALISTS["summary"])

    return ask(request, system=system_prompt)


# 3. Parallelization: independent calls at the same time
def parallel(topics):
    with ThreadPoolExecutor(max_workers=4) as ex:
        return list(
            ex.map(
                lambda t: ask(
                    f"One-line summary of: {t}",
                    max_tokens=80
                ),
                topics
            )
        )


# 4. Orchestrator-workers: one call plans, others execute,
# and one final call combines their results
def orchestrate(topic):
    plan = ask(
        f"List 3 subtopics of {topic}, one per line, no numbering.",
        max_tokens=80
    ).splitlines()

    plan = [p.strip() for p in plan if p.strip()][:3]

    with ThreadPoolExecutor(max_workers=3) as ex:
        parts = list(
            ex.map(
                lambda s: ask(
                    f"Explain {s} in 2 sentences.",
                    max_tokens=150
                ),
                plan
            )
        )

    return ask(
        "Combine these into one short study note:\n"
        + "\n".join(parts)
    )


# 5. Evaluator-optimizer: write, critique, revise
def refine(task, rounds=3):
    draft = ask(task)

    for _ in range(rounds):
        critique = ask(
            f"Task: {task}\n"
            f"Draft: {draft}\n"
            "If the draft fully meets the task, reply only PASS. "
            "Otherwise give 2 specific fixes.",
            max_tokens=150
        )

        if critique.strip().upper().startswith("PASS"):
            break

        draft = ask(
            f"Task: {task}\n"
            f"Draft: {draft}\n"
            f"Fixes: {critique}\n"
            "Write the improved draft."
        )

    return draft


if __name__ == "__main__":
    print("1. Prompt chaining")
    print(chain("Artificial Intelligence"))

    print("\n2. Routing")
    print(route("Explain what an API is"))

    print("\n3. Parallelization")
    for result in parallel(["HTTP", "DNS", "TCP", "IP"]):
        print(result)

    print("\n4. Orchestrator-workers")
    print(orchestrate("Computer Networks"))

    print("\n5. Evaluator-optimizer")
    print(refine("Explain the difference between HTTP and HTTPS."))
