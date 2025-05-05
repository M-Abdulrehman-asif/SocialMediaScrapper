import os
from fastapi import FastAPI
from pydantic import BaseModel
from apify_client import ApifyClientAsync
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_TOKEN')
if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN environment variable not set.")

app = FastAPI()

class KeywordRequest(BaseModel):
    keywords: list[str]


async def facebook_crawl(keyword: str, limit: int = 1):
    print(f"Scraping Facebook posts for keyword: {keyword}")
    apify_client = ApifyClientAsync(APIFY_TOKEN)
    try:
        actor_client = apify_client.actor('axesso_data/facebook-posts-scraper')
        call_result = await actor_client.call(run_input={
            "startUrls": [{"url": f"https://www.facebook.com/hashtag/{keyword}"}],
            "resultsLimit": limit
        })

        if not call_result:
            return {"error": f"No data found for facebook keyword: {keyword}"}

        dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
        list_page = await dataset_client.list_items()

        if not list_page.items:
            return {"error": f"No data found for facebook keyword: {keyword}"}

        return list_page.items

    except Exception as e:
        print(f"Facebook crawl error: {type(e).__name__}: {e}")
        return []
