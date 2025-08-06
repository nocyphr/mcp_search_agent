from os import getenv
import requests
import asyncio


async def fetch_scrape(session, url):
    headers = {
        "X-API-KEY": getenv("FIRECRAWL_API_KEY"),
        "Content-Type": "application/json",
    }
    payload = {"url": url, "formats": ["markdown"]}
    async with session.post(
        getenv("FIRECRAWL_SCRAPE_URL"), json=payload, headers=headers, timeout=20
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data.get("data", {}).get("markdown", "")


async def extract_with_llm(markdown: str):
    import litellm

    with open("src/prompts/extraction_prompt.md") as f:
        prompt = f.read().format(markdown=markdown)
    try:
        response = await litellm.acompletion(
            model=getenv("EXTRACTION_MODEL"),
            messages=[{"role": "user", "content": prompt}],
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception:
        return "NONE"


async def enrich_with_markdown_async(results):
    import aiohttp

    async with aiohttp.ClientSession() as session:
        tasks = [
            (
                fetch_scrape(session, item["url"])
                if "url" in item
                else asyncio.sleep(0, result="")
            )
            for item in results
        ]
        markdowns = await asyncio.gather(*tasks)

        extract_tasks = [extract_with_llm(markdown) for markdown in markdowns]
        extracts = await asyncio.gather(*extract_tasks)

        for item, extract in zip(results, extracts):
            item["markdown"] = extract
    return results


def firecrawl_search(query: str, limit: int = 20) -> dict:
    payload = {"query": query, "limit": limit}
    headers = {"X-API-KEY": getenv("FIRECRAWL_API_KEY")}
    resp = requests.post(
        getenv("FIRECRAWL_SEARCH_URL"), json=payload, headers=headers, timeout=10
    )
    resp.raise_for_status()
    return resp.json()
