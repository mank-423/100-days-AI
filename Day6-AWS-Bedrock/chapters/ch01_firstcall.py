from client import client, MODEL

# --- Part A: the simplest call ---
msg = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    system="You are Pagewise, a friendly study assistant. Explain simply.",
    messages=[{"role": "user", "content": "In 3 sentences, what is a context window?"}],
)

# Responses are a LIST of content blocks, not a plain string
text = next(b.text for b in msg.content if b.type == "text")
print(text)
print("stop_reason:", msg.stop_reason)
print("usage:", msg.usage)

# --- Part B: memory is YOUR job ---
history = [
    {"role": "user", "content": "My name is Asha and I'm studying biology."},
]
reply = client.messages.create(model=MODEL, max_tokens=300, messages=history)
history.append({"role": "assistant", "content": reply.content})
history.append({"role": "user", "content": "What did I say I was studying?"})

reply2 = client.messages.create(model=MODEL, max_tokens=300, messages=history)
print(next(b.text for b in reply2.content if b.type == "text"))