import time
from client import client, MODEL

chapters = {'ch1': 'Cells are the basic unit of life.', 'ch2': 'DNA stores genetic information.'}

# batch creation
batch = client.messages.batches.create(requests=[{
    'custom_id': cid,
    'params': {'model': MODEL, 'max_tokens': 200, 'messages': [{'role': 'user', 'content': f'Write 1 quiz question about: {txt}'}]}}
    for cid, txt in chapters.items()
])

print('batch id:', batch.id)


# while batch creation not completed vs completed
while client.messages.batches.retrieve(batch.id).processing_status != 'ended':
    time.sleep(30)

for item in client.messages.batches.results(batch.id):
    if item.result.type == 'succeeded':
        print(item.custom_id, item.result.message.content[0].text)
    else:
        print(item.custom_id, 'failed:', item.result.type)