from os import getenv
import requests
import asyncio


async def fetch_scrape(session, url):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {"url": url, "formats": ["markdown"]}
    async with session.post(
        getenv("API_SCRAPE_URL"), json=payload, headers=headers, timeout=20
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data.get("data", {}).get("markdown", "")


async def extract_with_llm(markdown: str):
    import litellm

    prompt = f"""
Extract relevant information in a bulletpoint list from the content below.
If information is present, state it directly and concisely, with no introductory wording.
If markdown is a tutorial/instruction make sure you do not remove any information or change the sequence!
If you find something that sounds like it could be a quote, ensure its unchanged integrity. 
If you find code, make sure you ensure its unchanged integrity
a chain of thought should become an ordered list

---

RAW:
{markdown}
        """
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


def web_search(query: str, limit: int = 20) -> dict:
    payload = {"query": query, "limit": limit}
    resp = requests.post(getenv("API_SEARCH_URL"), json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()
