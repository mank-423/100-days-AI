from client import client, MODEL, text_of

f = client.beta.files.upload(file=('bio.pdf', open('chapters/bio.pdf', 'rb'),'application/pdf'))

print('file id:', f.id)

r = client.beta.messages.create(
    model=MODEL, max_tokens=400,
    betas=['files-api-2025-04-14'],
    messages=[
        {'role': 'user', 'content': [
        {'type': 'document', 'source': {'type': 'file', 'file_id': f.id}},
        {'type': 'text', 'text': 'Summarize this in 3 bullets.'},
    ]}],
)

print(text_of(r))
for item in client.beta.files.list():
    print(item.id, item.filename)
