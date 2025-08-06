from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
import os


app = FastAPI()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_CSE_CX = os.environ.get("GOOGLE_CSE_CX")


class ScrapePayload(BaseModel):
    url: str
    urls: List[str] = Field(default_factory=list)
    browser_config: dict = Field(default_factory=lambda: {
        "type": "BrowserConfig",
        "params": {"headless": True}
    })
    crawler_config: dict = Field(default_factory=lambda: {
        "type": "CrawlerRunConfig",
        "params": {"stream": False, "cache_mode": "bypass"}
    })

    @model_validator(mode='after')
    def set_urls(self):
        if not self.urls:
            self.urls = [self.url]
        return self

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data.pop('url', None)
        return data


class ScrapeRequest(BaseModel):
    url: str


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/scrape")
def scrape_endpoint(request: ScrapeRequest):
    try:
        payload = ScrapePayload(url=request.url)

        response = requests.post(
            "http://crawl4ai:11235/crawl",
            json=payload.model_dump()
        )
        response.raise_for_status()

        res = response.json()
        markdown = res.get('results')[0].get('markdown').get('raw_markdown')

        return {
            "data": {
                "url": request.url,
                "markdown": markdown
            },
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10


def google_api_search(query: str, limit: int = 20) -> List[dict]:
    if not GOOGLE_API_KEY or not GOOGLE_CSE_CX:
        err_msg: str = 'Missing GOOGLE_API_KEY or GOOGLE_CSE_CX in .env'
        raise RuntimeError(err_msg)

    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_CX,
        "num": min(limit, 10)  # CSE max per request
    }
    google_api_url: str = 'https://www.googleapis.com/customsearch/v1'
    resp = requests.get(google_api_url, params=params)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "description": item.get("snippet"),
            "url": item.get("link")
        })

    return results


@app.post("/search")
def search_endpoint(request: SearchRequest):
    try:
        results = google_api_search(request.query, request.limit)
        return {
            "success": True,
            "query": request.query,
            "limit": request.limit,
            "data": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
