from mcp.server.fastmcp import FastMCP
from utils import firecrawl_search, enrich_with_markdown_async, fetch_scrape
import os
import asyncio


mcp = FastMCP(
    host="0.0.0.0", port=int(os.getenv("TOOL_MCP_PORT", 8999)), log_level="INFO"
)


@mcp.tool()
def online_search(query: str, limit: int = 20) -> list:
    """
    Perform web search and enrich results with scraped markdown content.

    This function executes a web search using the Firecrawl search API, then
    enriches each search result by scraping the full webpage content and
    converting it to markdown format. Each result becomes a dictionary
    containing both the original search metadata and the scraped content.

    Parameters
    ----------
    query : str
        The search query string to find relevant web pages.
    limit : int, optional
        Maximum number of search results to return and enrich, by default 20.

    Returns
    -------
    list
        A list of dictionaries, where each dictionary represents an enriched
        search result containing the original search metadata plus scraped
        markdown content from the webpage.
    """
    results = firecrawl_search(query=query, limit=limit)
    if not results.get("success"):
        raise Exception(f"Error: Firecrawl search for -> {query} <- failed")
    docs = results.get("data", [])
    if not docs:
        raise Exception(
            f"Error: Firecrawl search for -> {query} <- returned no results"
        )
    return asyncio.run(enrich_with_markdown_async(docs))


@mcp.tool()
async def fetch_webpage(url: str) -> str:
    """
    Scrape a webpage and extract relevant information using AI-powered content analysis.

    This function performs a three-step process: scrapes webpage content using the
    Firecrawl API service, converts the scraped content to markdown format, and uses
    an LLM to extract and summarize key information into bullet points.

    Parameters
    ----------
    url : str
        The URL of the webpage to scrape and analyze. Must be a valid HTTP/HTTPS URL.

    Returns
    -------
    str
        A bullet-point formatted string containing the extracted relevant information
        from the webpage. If the content is a tutorial or instructions, the original
        sequence and completeness are preserved. Returns an empty string if scraping
        fails or encounters errors.
    """
    import aiohttp

    async with aiohttp.ClientSession() as session:
        return await fetch_scrape(session, url)


if __name__ == "__main__":
    mcp.run("streamable-http")
