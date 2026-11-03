import asyncio
from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

load_dotenv()

async def main():
    options = ClaudeAgentOptions(
        system_prompt='You are pagewise. Be concise.',
        allowed_tools = ['Read', 'Write', 'Glob'],
        permission_mode='acceptEdits', # auto-approve file edits; keep tools few
        max_turns = 6, #capping the loop
        model='claude-haiku-4-5-20251001',
        cwd='workspace', 
    )

    async for message in query(prompt='Read notes.txt and write summary.md with 3 bullets', options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

        elif isinstance(message, ResultMessage):
            print('cost:', getattr(message, 'total_cost_usd', None), 'turns:', getattr(message, 'num_turns', None))

asyncio.run(main())