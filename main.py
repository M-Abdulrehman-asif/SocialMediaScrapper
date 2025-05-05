from fastapi import FastAPI
from router.index import router as scrape_data_router

app = FastAPI(title="Social Media Scraper App")

app.include_router(scrape_data_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
