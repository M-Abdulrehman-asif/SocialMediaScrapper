from fastapi import APIRouter, Request
from datetime import datetime
from database.db_manager import DatabaseHandler
from crawlers.tiktok_crawl import tiktok_crawl
from crawlers.twitter_crawl import twitter_crawl
from utils.insert import insert_scraped_data, PLATFORM_MODEL_MAP

router = APIRouter()

@router.post("/scrape")
async def scrape_keywords(request: Request):
    print("[DEBUG] Received /scrape POST request")

    body = await request.json()
    print(f"[DEBUG] Request body: {body}")

    keywords = body.get("keywords")
    start_date_str = body.get("start_date")
    end_date_str = body.get("end_date")
    scrappers = body.get("scrappers")
    num_of_posts = body.get("num_of_posts")
    db_name = body.get("db_name")

    print(f"[DEBUG] Extracted keywords: {keywords}")
    print(f"[DEBUG] Start date string: {start_date_str}, End date string: {end_date_str}")
    print(f"[DEBUG] Scrappers to use: {scrappers}, Num of posts: {num_of_posts}, DB Name: {db_name}")

    try:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        print(f"[DEBUG] Parsed start_date: {start_date}, end_date: {end_date}")
    except ValueError as e:
        print(f"[ERROR] Date parsing failed: {e}")
        return {"error": "Invalid date format"}

    print("[DEBUG] Initializing database handler...")
    db_handler = DatabaseHandler(db_name=db_name)
    db_handler.connect_db()
    db_handler.create_db()
    db_handler.init_db()
    print("[DEBUG] Database setup completed")

    all_data = {}

    if 'tiktok' in scrappers:
        print(f"[INFO] Starting TikTok crawl for keywords: {keywords}")
        raw_data = await tiktok_crawl(keywords, num_of_posts)
        print(f"[DEBUG] TikTok raw data: {raw_data}")
        all_data.update(raw_data)

        with db_handler.session as db:
            print("[DEBUG] Inserting TikTok data into database...")
            insert_scraped_data(db, raw_data, PLATFORM_MODEL_MAP)
            print("[DEBUG] Data insertion completed")
            db.commit()
            print("[DEBUG] Database commit completed")

    if 'twitter' in scrappers:
        print(f"[INFO] Starting Twitter crawl for keywords: {keywords}")
        raw_data = await twitter_crawl(keywords, num_of_posts)
        print(f"[DEBUG] Twitter raw data: {raw_data}")

        # Wrap Twitter data under the 'twitter' platform name
        twitter_data = {keyword: {"twitter": raw_data[keyword]} for keyword in raw_data}
        all_data.update(twitter_data)

        with db_handler.session as db:
            print("[DEBUG] Inserting Twitter data into database...")
            insert_scraped_data(db, twitter_data, PLATFORM_MODEL_MAP)
            print("[DEBUG] Data insertion completed")
            db.commit()
            print("[DEBUG] Database commit completed")

    print("[INFO] Scraping process completed")
    return {"scraped_data": all_data}


from fastapi import Query
from typing import List
from crawlers.instagram_crawl import instagram_crawl

@router.post("/crawlinsta")
async def crawl_instagram(
    keywords: List[str] = Query(..., description="List of keywords"),
    num_of_posts: int = 1
):
    return await instagram_crawl(keywords, num_of_posts)
