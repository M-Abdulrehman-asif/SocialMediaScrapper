from utils.model import UserProfile, TwitterPost, InstaPost, FacebookPost

PLATFORM_MODEL_MAP = {
    "tiktok": UserProfile,
    "twitter": TwitterPost,
    "instagram":InstaPost,
    "facebook":FacebookPost
}


def insert_data(db, raw_data, platform_model_map):
    print("[DEBUG] Starting insert_scraped_data function")

    default_platform = None
    if len(platform_model_map) == 1:
        default_platform = list(platform_model_map.keys())[0]

    for keyword, platform_data in raw_data.items():
        print(f"[INFO] Processing keyword: {keyword}")

        if isinstance(platform_data, dict) and "error" in platform_data:
            print(f"[WARNING] Skipping keyword '{keyword}' due to error: {platform_data['error']}")
            continue

        if isinstance(platform_data, dict):
            for platform_name, items in platform_data.items():
                print(f"[DEBUG] Processing platform: {platform_name}")

                if not isinstance(items, list):
                    items = [items]

                model_class = platform_model_map.get(platform_name.lower())
                if not model_class:
                    print(f"[WARNING] Unknown platform '{platform_name}', skipping.")
                    continue

                for index, item in enumerate(items, start=1):
                    print(f"[DEBUG] Processing item {index}: {item}")
                    try:
                        obj = model_class(**item)
                        db.add(obj)
                        print(f"[DEBUG] Added {platform_name} object to session: {obj}")
                    except Exception as e:
                        print(f"[ERROR] Failed to create/add {platform_name} object: {e}")

        elif isinstance(platform_data, list):
            print(f"[DEBUG] Detected list. Attempting to use default platform")

            if not default_platform:
                print("[ERROR] No default platform defined for raw list data.")
                continue

            model_class = platform_model_map.get(default_platform)
            for index, item in enumerate(platform_data, start=1):
                print(f"[DEBUG] Processing item {index}: {item}")
                try:
                    obj = model_class(**item)
                    db.add(obj)
                    print(f"[DEBUG] Added {default_platform} object to session: {obj}")
                except Exception as e:
                    print(f"[ERROR] Failed to create/add {default_platform} object: {e}")

        else:
            print(f"[WARNING] Unexpected data format for keyword '{keyword}': {type(platform_data).__name__}")

    try:
        db.commit()
        print("[DEBUG] Successfully committed data to the database")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Commit failed, rolled back transaction: {e}")
