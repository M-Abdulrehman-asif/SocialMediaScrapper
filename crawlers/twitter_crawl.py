import os
from apify_client import ApifyClientAsync
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_TOKEN')

if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN environment variable not set.")

def extract_twitter_fields(item):
    print("[DEBUG] Extracting fields from item...")
    media = (
        item.get("extended_entities", {})
        .get("media", [{}])
    )
    return {
        "channel_name": item.get("user", {}).get("name"),
        "description": item.get("full_text") or item.get("text") or "",
        "likes_count": item.get("favorite_count"),
        "retweets_count": item.get("retweet_count"),
        "media_url": media[0].get("media_url_https") if media else None,
        "favorite_count": item.get("favorite_count"),
        "followers_count": item.get("user", {}).get("followers_count"),
    }


async def twitter_crawl(keywords: list, num_of_posts: int):
    print(f"[INFO] Starting Twitter crawl for keywords: {keywords}")
    apify_client = ApifyClientAsync(APIFY_TOKEN)

    all_data = {}

    try:
        for keyword in keywords:
            print(f"\n[INFO] Processing keyword: {keyword}")
            platform_data = []

            print("[DEBUG] Instantiating Twitter actor client...")
            actor_client = apify_client.actor('quacker/twitter-profile-search')

            print(f"[DEBUG] Calling actor with keyword: '{keyword}' and limit: {num_of_posts}")
            call_result = await actor_client.call(run_input={
                "searchTerms": [keyword],
                "resultsLimit": num_of_posts
            })

            print(f"[DEBUG] Actor call result: {call_result}")

            if not call_result or 'defaultDatasetId' not in call_result:
                print(f"[ERROR] No run result or missing dataset ID for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for Twitter keyword: {keyword}"}
                continue

            dataset_id = call_result['defaultDatasetId']
            print(f"[DEBUG] Fetching dataset with ID: {dataset_id}")
            dataset_client = apify_client.dataset(dataset_id)

            list_page = await dataset_client.list_items()
            print(f"[DEBUG] Retrieved {len(list_page.items)} items from dataset")

            if not list_page.items:
                print(f"[INFO] No items found in dataset for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for Twitter keyword: {keyword}"}
                continue

            for idx, item in enumerate(list_page.items[:num_of_posts], start=1):
                print(f"[DEBUG] Processing item {idx}: {item}")
                extracted = extract_twitter_fields(item)
                print(f"[DEBUG] Extracted data: {extracted}")
                platform_data.append(extracted)

            all_data[keyword] = {"twitter": platform_data}
            print(f"[INFO] Completed processing for keyword: {keyword}, Total items: {len(platform_data)}")

        print(f"[INFO] Twitter crawl completed for all keywords.")
        return all_data

    except Exception as e:
        print(f"[EXCEPTION] Twitter crawl failed: {type(e).__name__}: {e}")
        return {"error": str(e)}
