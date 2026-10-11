import json
from pathlib import Path
from client import client, MODEL

tools = [
    {
        "name": "create_flashcards",
        "description": "Save study flashcards made from the material.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cards": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "answer": {"type": "string"},
                        },
                        "required": ["question", "answer"],
                    },
                }
            },
            "required": ["cards"],
        },
    }
]

notes = Path(__file__).parent.joinpath("book.txt").read_text(encoding="utf-8")[:6000]

r = client.messages.create(
    model=MODEL,
    max_tokens=1000,
    tools=tools,
    tool_choice={"type": "tool", "name": "create_flashcards"},
    messages=[{'role': 'user', 'content': f'Make 5 flashcards from this:\n{notes}'}],
)

cards = next(b.input for b in r.content if b.type == 'tool_use')['cards']
json.dump(cards, open('flashcards.json', 'w'), indent=2)
print(len(cards), 'cards saved')