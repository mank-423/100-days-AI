from client import client, MODEL

q = 'A tank fills in 6 hours with pipe A and 9 hours with pipe B. A drain empties it in 12 hours. With all three open, how long to fill?'

r = client.messages.create(
    model=MODEL,
    max_tokens=4000, # must be bigger than the budget
    thinking={'type': 'enabled', 'budget_tokens': 2000}, # minimum is 1024
    messages=[{'role': 'user', 'content': q}],
)

for b in r.content:
    if b.type == 'thinking':
        print('THINKING:', b.thinking[:300], '....')
    elif b.type == 'text':
        print('ANSWER:', b.text)

#Usage
print(r.usage)