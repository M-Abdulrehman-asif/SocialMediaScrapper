import os
from apify_client import ApifyClientAsync
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_TOKEN')

if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN environment variable not set.")


def clean_facebook_data(raw_data: dict) -> dict:
    cleaned_data = {}

    for keyword, platforms in raw_data.items():
        facebook_data = platforms.get("facebook")
        if not facebook_data:
            cleaned_data[keyword] = {"error": "No Facebook data available"}
            continue

        cleaned_facebook = []

        for item in facebook_data:
            try:
                cleaned_item = {
                    "facebook_url": item["facebookUrl"],
                    "reaction": item.get("reaction"),
                    "name": item.get("name"),
                    "profile_url": item.get("profileUrl"),
                    "facebook_id": item.get("facebookId")
                }
                cleaned_facebook.append(cleaned_item)
            except KeyError as e:
                print(f"[WARN] Missing field in item: {e}")
                continue

        cleaned_data[keyword] = {"facebook": cleaned_facebook}

    return cleaned_data


async def facebook_crawl(keywords: list, num_of_posts: int):
    print(f"[INFO] Starting facebook crawl for keywords: {keywords}")
    apify_client = ApifyClientAsync(APIFY_TOKEN)

    all_data = {}

    try:
        for keyword in keywords:
            print(f"\n[INFO] Processing keyword: {keyword}")
            platform_data = {}

            print("[DEBUG] Calling Apify actor: apify/facebook-likes-scraper")
            actor_client = apify_client.actor('apify/facebook-likes-scraper')

            call_result = await actor_client.call(run_input={
                "startUrls": [{"url": f"https://www.facebook.com/{keyword}"}],
                "resultsLimit": num_of_posts
            })

            if not call_result or 'defaultDatasetId' not in call_result:
                print(f"[ERROR] No run result or missing dataset ID for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for facebook keyword: {keyword}"}
                continue

            dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
            list_page = await dataset_client.list_items()

            if not list_page.items:
                print(f"[INFO] No items found in dataset for keyword: {keyword}")
                all_data[keyword] = {"error": f"No data found for facebook keyword: {keyword}"}
                continue

            platform_data["facebook"] = list_page.items[:1]
            print(f"[INFO] Total facebook data count (after limit): {len(platform_data['facebook'])}")
            all_data[keyword] = platform_data

        cleaned = clean_facebook_data(all_data)
        return cleaned

    except Exception as e:
        print(f"[EXCEPTION] Facebook crawl failed: {type(e).__name__}: {e}")
        return {"error": str(e)}
