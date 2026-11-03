
from client import client, MODEL, text_of


# Connect Claude to a remote MCP server
response = client.beta.messages.create(
    model=MODEL,
    max_tokens=800,

    # Enable Anthropic's MCP connector
    betas=["mcp-client-2025-11-20"],

    # Define the remote MCP server
    mcp_servers=[
        {
            "type": "url",
            "url": "https://example-server.modelcontextprotocol.io/sse",
            "name": "example-mcp",
        }
    ],

    # Enable the tools provided by that server
    tools=[
        {
            "type": "mcp_toolset",
            "mcp_server_name": "example-mcp",
        }
    ],

    messages=[
        {
            "role": "user",
            "content": "What tools are available to you? Explain what they do."
        }
    ],
)


# Print the response
for block in response.content:
    if block.type == "text":
        print(block.text)

    elif block.type == "mcp_tool_listing":
        print("\nAvailable MCP tools:")
        for tool in block.tools:
            print(f"\nName: {tool.name}")
            print(f"Description: {tool.description}")
