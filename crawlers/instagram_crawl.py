import os
from apify_client import ApifyClientAsync
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_TOKEN')

if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN environment variable not set.")


def clean_instagram_data(raw_data: dict) -> dict:
    cleaned_data = {}

    for keyword, platforms in raw_data.items():
        instagram_data = platforms.get("instagram")
        if not instagram_data:
            cleaned_data[keyword] = {"error": "No Instagram data available"}
            continue

        cleaned_instagram = []
        for item in instagram_data:
            cleaned_item = {
                "name": item.get("name"),
                "posts_count": item.get("postsCount"),
                "url": item.get("url"),
                "posts": item.get("posts"),
                "posts_per_day": item.get("postsPerDay")
            }
            cleaned_instagram.append(cleaned_item)

        cleaned_data[keyword] = {"instagram": cleaned_instagram}

    return cleaned_data


async def instagram_crawl(keywords: list, num_of_posts: int) -> dict:
    print(f"[INFO] Starting Instagram crawl for keywords: {keywords}")
    apify_client = ApifyClientAsync(APIFY_TOKEN)

    all_data = {}

    try:
        for keyword in keywords:
            print(f"\n[INFO] Processing keyword: {keyword}")
            platform_data = {}

            print("[DEBUG] Calling Apify actor: apify/instagram-search-scraper")
            actor_client = apify_client.actor('apify/instagram-search-scraper')

            call_result = await actor_client.call(run_input={
                "searchQuery": keyword,
                "resultsLimit": num_of_posts,
                "maxRequestPages": 1,
                "searchMode": "hashtag",
                "resultsType": "posts",
            })
            print(call_result)

            if not call_result or 'defaultDatasetId' not in call_result:
                print(f"[ERROR] No run result or missing dataset ID for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for Instagram keyword: {keyword}"}
                continue

            dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
            list_page = await dataset_client.list_items()

            if not list_page.items:
                print(f"[INFO] No items found in dataset for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for Instagram keyword: {keyword}"}
                continue

            platform_data["instagram"] = list_page.items[:num_of_posts]
            print(f"[INFO] Total Instagram data count (after limit): {len(platform_data['instagram'])}")
            all_data[keyword] = platform_data

        cleaned_data = clean_instagram_data(all_data)

        return {
            "status": "success",
            "scraped_data": cleaned_data
        }

    except Exception as e:
        print(f"[EXCEPTION] Instagram crawl failed: {type(e).__name__}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
