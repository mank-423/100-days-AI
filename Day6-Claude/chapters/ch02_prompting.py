from pathlib import Path
from client import MODEL, client, text_of

notes = Path(__file__).parent.joinpath("book.txt").read_text(encoding="utf-8")[:6000]

SYSTEM = '''
You are Pagewise, a study-assistant for a first year biology student. 
Rules: 
- Explain in plain language, then give one concrete example.
- If the answer is not in the material say so instead of guessing.
- Keep answers under 120 words
'''

vague='Explain this'
sharp = f'''<material>
{notes}
</material>
<task>Explain the main idea of the material.</task>
<example>
Q. What is osmosis?
A: Water moving across a membrane toward the saltier side. Example: a raisin
swelling in water.
</example>
'''

for p in (vague, sharp):
    r = client.messages.create(model=MODEL, max_tokens=400, system=SYSTEM,
    messages=[{'role': 'user', 'content': p}])
    print(text_of(r))
    print('-' * 40)
