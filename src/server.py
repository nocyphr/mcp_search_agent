from mcp.server.fastmcp import FastMCP
import os

from llama_index.tools.mcp import McpToolSpec, BasicMCPClient
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI


mcp = FastMCP(host="0.0.0.0", port=os.getenv("MCP_PORT", 8000), log_level="INFO")


@mcp.tool()
async def search(query: str):
    """
    this is a docstring placeholder
    """
    client = BasicMCPClient(f"http://tool-server:{os.getenv('TOOL_MCP_PORT')}/mcp", timeout=120)
    spec = McpToolSpec(client=client)

    tools = await spec.to_tool_list_async()

    llm = OpenAI(model="gpt-4o")
    agent = ReActAgent(tools=tools, llm=llm)
    ctx = Context(agent)
    handler = agent.run(
        f"""
this is a placeholder
""",
        ctx=ctx,
    )

    response = await handler
    print(str(response))

if __name__ == "__main__":
    mcp.run('streamable-http')
