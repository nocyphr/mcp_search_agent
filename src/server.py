from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from llama_index.llms.litellm import LiteLLM
from llama_index.tools.mcp import McpToolSpec, BasicMCPClient
from mcp.server.fastmcp import FastMCP
import os

from datetime import datetime


mcp = FastMCP(host="0.0.0.0", port=os.getenv("MCP_PORT", 8000), log_level="INFO")


@mcp.tool()
async def search(query: str):
    """
    search: a smart search tool for internet research
    """
    client = BasicMCPClient(
        f"http://tool-server:{os.getenv('TOOL_MCP_PORT')}/mcp", timeout=120
    )
    spec = McpToolSpec(client=client)

    tools = await spec.to_tool_list_async()

    llm = LiteLLM(model=os.getenv("AGENT_MODEL"))
    agent = ReActAgent(tools=tools, llm=llm)
    ctx = Context(agent)
    print("CAVEMAN", datetime.now())
    handler = agent.run(
        f"""
{query}
""",
        ctx=ctx,
    )

    response = await handler
    print(str(response))
    return str(response)


if __name__ == "__main__":
    mcp.run("streamable-http")
