import os
from apify_client import ApifyClientAsync
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_TOKEN')

if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN environment variable not set.")


def clean_instagram_data(all_data):
    cleaned_data = {}

    for keyword, platform_data in all_data.items():
        if "error" in platform_data:
            cleaned_data[keyword] = {"error": platform_data["error"]}
            continue

        raw_data_list = platform_data.get("instagram", [])
        if not raw_data_list:
            cleaned_data[keyword] = {"error": "No Instagram data found."}
            continue

        item = raw_data_list[0]  # Only first post as you requested
        cleaned_data[keyword] = {
            "name": item.get("name"),
            "posts_count": item.get("postsCount"),
            "top_post": {
                "url": item.get("url"),
                "likes_count": item.get("likesCount"),
                "comments_count": item.get("commentsCount")
            }
        }

    return cleaned_data


async def instagram_crawl(keywords: list, num_of_posts: int):
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
                "resultsLimit": num_of_posts
            })

            if not call_result or 'defaultDatasetId' not in call_result:
                print(f"[ERROR] No run result or missing dataset ID for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for Instagram keyword: {keyword}"}
                continue

            dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
            list_page = await dataset_client.list_items()

            if not list_page.items:
                print(f"[INFO] No items found in dataset for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for instagram keyword: {keyword}"}
                continue

            platform_data["instagram"] = list_page.items[:1]
            print(f"[INFO] Total Instagram data count (after limit): {len(platform_data['instagram'])}")
            all_data[keyword] = platform_data

        cleaned = clean_instagram_data(all_data)
        return cleaned
        # return all_data

    except Exception as e:
        print(f"[EXCEPTION] Instagram crawl failed: {type(e).__name__}: {e}")
        return {"error": str(e)}
