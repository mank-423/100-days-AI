from client import client, MODEL

USAGE = {
    'input': 0,
    'output': 0,
    'calls': 0,
}


def cost_usd(price_in=1.0, price_out=5.0):
    return USAGE['input'] / 1e6 * price_in + USAGE['output'] / 1e6 * price_out



def run_with_tools(messages, tools, handlers, system=None, max_turns=8, max_tokens=1024):
    for turn in range(max_turns):
        kwargs = dict(
            model=MODEL,
            max_tokens=max_tokens,
            messages=messages,
            tools=tools
        )

        if system:
            kwargs['system'] = system

        resp = client.messages.create(**kwargs)
        USAGE['input'] += resp.usage.input_tokens
        USAGE['output'] += resp.usage.output_tokens
        USAGE['calls'] += 1

        messages.append({'role': 'assistant', 'content': resp.content})

        if resp.stop_reason != 'tool_use':
            return resp

        results = []

        for b in resp.content:
            if b.type != 'tool_use':
                continue

            try:
                out, err = handlers[b.name](**b.input), False
            except Exception as e:
                out, err = f'Error: {e}', True

            item = {
                'type': 'tool_result',
                'tool_use_id': b.id,
                'content': str(out)
            }

            if err:
                item['is_error'] = True

            results.append(item)

        # Inside the outer loop
        messages.append({'role': 'user', 'content': results})

    # Outside the outer loop
    raise RuntimeError(f'stopped after {max_turns} turns')
