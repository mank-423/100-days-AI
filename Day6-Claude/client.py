import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(
    api_key=os.getenv("CLAUDE_API_KEY"),
)

MODEL = "claude-haiku-4-5-20251001" 

def text_of(message):
    return "".join(
        block.text
        for block in message.content
        if block.type == "text"
    )
