from pathlib import Path
from client import client, MODEL

text =  Path(__file__).parent.joinpath("book.txt").read_text(encoding="utf-8")[:6000]
doc = {
    'type': 'document',
    'source': {'type': 'text', 'media_type': 'text/plain', 'data': text},
    'title': 'Biology notes',
    'citations': {'enabled': True},
}
r = client.messages.create(
    model=MODEL, 
    max_tokens=250,
    messages=[{'role': 'user', 'content': [doc, {'type': 'text', 'text': 'What is the main claim? Answer in 2 sentences.'}]}],
)
for b in r.content:
    if b.type == 'text':
        print(b.text)
    for c in (b.citations or []):
        print(' SOURCE:', c.cited_text[:100])