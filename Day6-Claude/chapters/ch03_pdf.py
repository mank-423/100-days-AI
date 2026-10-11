import base64
from client import client, MODEL, text_of

pdf = base64.standard_b64encode(open('chapters/bio.pdf', 'rb').read()).decode()

r = client.messages.create(
    model=MODEL,
    max_tokens=600,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf,
                    },
                },
                {
                    "type": "text",
                    "text": "List the 5 key ideas, one line each. Mention any chart you see.",
                },
            ],
        }
    ],
)

print(text_of(r))
print(r.usage)