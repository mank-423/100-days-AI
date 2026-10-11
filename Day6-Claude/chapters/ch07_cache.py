from pathlib import Path
from client import client, MODEL

book = Path(__file__).parent.joinpath("book.txt").read_text(encoding="utf-8")

# We are using caching provided by claude

# What if we use redis as a cache, but that won't save us the cost. It will still take same amt of tokens as a normal call

# This shows no of tokens in total of the text file
n = client.messages.count_tokens(model=MODEL, messages=[{'role': 'user',
'content': book}])
print('book is', n.input_tokens, 'tokens')


# cache created
system = [
    {'type': 'text', 'text': 'You are Pagewise. Answer only from the book.'},
    {'type': 'text', 'text': book, 'cache_control': {'type': 'ephemeral'}},
    # cache up to here
    # for a 1-hour cache: {'type': 'ephemeral', 'ttl': '1h'}
]

#This will show how much tokens were read.
# Loop through the questions
for q in ['What is chapter 1 about?', 'Name one key term.', 'Give a quiz question.']:
    r = client.messages.create(model=MODEL, max_tokens=200, system=system, messages=[{'role': 'user', 'content': q}])
    u = r.usage
    print(q, '| written:', u.cache_creation_input_tokens, '| read:', u.cache_read_input_tokens)