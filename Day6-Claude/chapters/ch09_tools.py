
from client import text_of
from toolkit import run_with_tools

GLOSSARY = {
    'mitosis': 'Cell division that makes two identical cells.',
    'osmosis': (
        'Water moving across a membrane toward higher solute '
        'concentration.'
    ),
}


def lookup_term(term):
    return GLOSSARY.get(term.lower(), 'not found in glossary')


tools = [
    {
        'name': 'lookup_term',
        'description': (
            'Look up a biology term in the course glossary. '
            'Use it before explaining any term.'
        ),
        'input_schema': {
            'type': 'object',
            'properties': {
                'term': {
                    'type': 'string',
                    'description': 'One term, for example mitosis',
                }
            },
            'required': ['term'],
        },
    }
]

msgs = [
    {
        'role': 'user',
        'content': 'What does osmosis mean in our course?',
    }
]

final = run_with_tools(
    msgs,
    tools,
    {'lookup_term': lookup_term},
)

print(text_of(final))
print(len(msgs), 'messages in the conversation')
print("Conversation:",msgs)
# Expected flow:
# user → assistant (tool_use) → user (tool_result) → assistant
