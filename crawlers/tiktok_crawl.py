import os
from apify_client import ApifyClientAsync
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_TOKEN')

if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN environment variable not set.")

async def tiktok_crawl(keywords: list, num_of_posts: int):
    print(f"[INFO] Starting TikTok crawl for keywords: {keywords}")
    apify_client = ApifyClientAsync(APIFY_TOKEN)

    all_data = {}

    try:
        for keyword in keywords:
            print(f"\n[INFO] Processing keyword: {keyword}")
            platform_data = {}

            print("[DEBUG] Calling Apify actor: clockworks/tiktok-user-search-scraper")
            actor_client = apify_client.actor('clockworks/tiktok-user-search-scraper')

            call_result = await actor_client.call(run_input={
                "searchQuery": keyword,
                "resultsLimit": num_of_posts
            })

            if not call_result or 'defaultDatasetId' not in call_result:
                print(f"[ERROR] No run result or missing dataset ID for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for TikTok keyword: {keyword}"}
                continue

            dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
            list_page = await dataset_client.list_items()

            if not list_page.items:
                print(f"[INFO] No items found in dataset for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for TikTok keyword: {keyword}"}
                continue

            platform_data["tiktok"] = list_page.items[:1]
            print(f"[INFO] Total TikTok data count (after limit): {len(platform_data['tiktok'])}")
            all_data[keyword] = platform_data

        return all_data

    except Exception as e:
        print(f"[EXCEPTION] TikTok crawl failed: {type(e).__name__}: {e}")
        return {"error": str(e)}
