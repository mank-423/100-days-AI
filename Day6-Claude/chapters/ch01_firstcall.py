from client import client, MODEL, text_of

# model calling
msg = client.messages.create(
    model=MODEL,
    max_tokens=300,
    system='You are Pagewise, a friendly study assistant.',
    messages = [
        {'role': 'user', 'content': 'In 2 sentences, what is context window?'}
    ]
)

print(text_of(msg))
print(msg.stop_reason)
print(msg.usage)


# memory
history = [
    {'role': 'user', 'content': 'My name is Asha and I study biology.'}
]

r1 = client.messages.create(model = MODEL, max_tokens=200, messages=history)
history.append({'role': 'assistant', 'content': r1.content})
history.append({'role': 'user', 'content': 'What do I study?'})
r2 = client.messages.create(model=MODEL, max_tokens=200, messages=history)
print(text_of(r2))

# streaming: print words as they arrive
with client.messages.stream(model=MODEL, max_tokens=200, messages=[{'role': 'user', 'content': 'Explain tokens in 2 sentences.'}]) as s:
    for t in s.text_stream:
        print(t, end='', flush=True)