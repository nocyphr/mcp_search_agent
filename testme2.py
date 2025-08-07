import asyncio
from fastmcp import Client


async def run_search():
    async with Client("http://localhost:8000/mcp/") as client:
        res = await client.call_tool(
            "search", {"query": "How do I get clean llama-index react agent logs in a custom logger to file? Give me code examples. My reactagent is from llamaindex latest version (13) and is imported from workflows. it runs behind a fastmcp server as a tool. "}
        )
        if res.content:
            print(res.content[0].text)


asyncio.run(run_search())
