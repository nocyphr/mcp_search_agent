import asyncio
import os
from llama_index.tools.mcp import BasicMCPClient

async def main():
    MCP_PORT = os.getenv("MCP_PORT", "8080")
    client = BasicMCPClient(f"http://localhost:{MCP_PORT}/mcp")
    response = await client.call_tool("search", {"query": "What is the capital of France?"})
    print("=== Response ===")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())

