import os
from fastapi import FastAPI
from apify_client import ApifyClientAsync
from dotenv import load_dotenv

load_dotenv()
APIFY_TOKEN = os.getenv('APIFY_TOKEN')
if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN environment variable not set.")

app = FastAPI()

async def instagram_crawl(keyword: str, limit: int = 1):
    apify_client = ApifyClientAsync(APIFY_TOKEN)
    try:
        actor = apify_client.actor("apify/instagram-post-scraper")
        run_input = {"username": [keyword], "resultsLimit": limit}
        call_result = await actor.call(run_input=run_input)
        dataset_client = apify_client.dataset(call_result["defaultDatasetId"])
        items = await dataset_client.list_items()
        return items.items
    except Exception as e:
        print(f"Error during Instagram scraping: {e}")
        return {"error": str(e)}
