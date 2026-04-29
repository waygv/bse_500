from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import requests
import os

app = FastAPI()

# Serve static files (HTML, JS, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the frontend HTML at root
@app.get("/")
async def get_index():
    return FileResponse("static/index.html")


# Proxy to Yahoo Finance autocomplete endpoint
@app.get("/search")
async def search_stocks(q: str = ""):
    if not q:
        return JSONResponse(content={"quotes": []})

    yahoo_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(yahoo_url, headers=headers)
        return JSONResponse(content=response.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
