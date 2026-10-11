from client import client, MODEL

r = client.beta.messages.create(
    model=MODEL, max_tokens=1500,
    betas=['code-execution-2025-05-22'],
    tools=[{'type': 'code_execution_20250522', 'name': 'code_execution'}],
    messages=[{'role': 'user', 'content': 'Compute the mean and standard deviation of 12, 15, 9, 22, 18 using code.'}],
)

for b in r.content:
    print(b.type)
    if b.type == 'text':
        print(b.text)