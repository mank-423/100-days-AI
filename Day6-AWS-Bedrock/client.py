import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

REGION = "ap-south-1"

client = Anthropic(
    base_url=f"https://bedrock-mantle.{REGION}.api.aws/anthropic",
    api_key=os.getenv("API_KEY"),
)

key = os.getenv("API_KEY")
print("Key exists:", key is not None)
print("Key prefix:", key[:10] if key else None)

MODEL = "anthropic.claude-sonnet-5"  # or "anthropic.claude-haiku-4-5" to save money