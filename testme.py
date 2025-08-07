import asyncio
from fastmcp import Client

async def run_search():
    async with Client("http://localhost:8000/mcp/") as client:
        res = await client.call_tool(
            "search", {"query": "What is the capital of France?"}
        )
        if res.content:
            print(res.content[0].text)


asyncio.run(run_search())
