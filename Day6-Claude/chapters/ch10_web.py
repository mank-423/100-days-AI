from client import client, MODEL

r = client.messages.create(
    model=MODEL,
    max_tokens=1000,
    tools=[
        {'type': 'web_search_20250305', 'name': 'web_search', 'max_uses': 2}
    ],
    messages=[
        {'role': 'user', 'content': 'What is new in the field of CRISPR gene editing this year? 3 bullets.'}
    ]
)

for b in r.content:
    if b.type == 'text':
        print(b.text)

print(r.usage)


#web fetch
r2 = client.beta.messages.create(
    model=MODEL,
    max_tokens=1000,
    betas=['web-fetch-2025-09-10'],
    tools=[
        {
            'type': 'web_fetch_20250910',
            'name': 'web_fetch',
            'max_uses': 1,
        }
    ],
    messages=[
        {
            'role': 'user',
            'content': 'Summarize https://mayank-kl2e.onrender.com/ in one sentence.',
        }
    ],
)

print([b.type for b in r2.content])