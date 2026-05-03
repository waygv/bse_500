import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

import yfinance as yf
from src.analysis.heatmap import build_heatmap_figures
from src.graph.trading_graph import build_trading_graph

from src.scrapers.bse_500_watchlist import scrape_bse_500_watchlist
from src.scrapers.bse_industry import scrape_bse_industry

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown tasks correctly using the lifespan pattern."""
    print("STARTUP: Checking market data files...")
    marketwatch_path = "data/processed/MarketWatch.csv"
    index_path = "data/processed/Index.csv"
    
    # Ensure processed directory exists
    os.makedirs("data/processed", exist_ok=True)
    
    if not os.path.exists(marketwatch_path) or not os.path.exists(index_path):
        print("STARTUP: Market data missing. Attempting background download...")
        # Run in background to not block server start
        asyncio.create_task(asyncio.to_thread(scrape_bse_500_watchlist))
        asyncio.create_task(asyncio.to_thread(scrape_bse_industry))
    else:
        print("STARTUP: Market data files already present.")
        
    yield
    print("SHUTDOWN: Cleaning up...")

app = FastAPI(title="BSE TradingAgents Terminal", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

@app.get("/api/heatmap")
async def heatmap_data():
    try:
        marketwatch_path = "data/processed/MarketWatch.csv"
        index_path = "data/processed/Index.csv"
        
        if not os.path.exists(marketwatch_path) or not os.path.exists(index_path):
             return JSONResponse(content={"error": "data_missing", "index_fig": None, "market_fig": None})

        index_fig, market_fig = await asyncio.to_thread(build_heatmap_figures)
        return JSONResponse(content={
            "index_fig": json.loads(index_fig.to_json()),
            "market_fig": json.loads(market_fig.to_json()),
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e), "index_fig": None, "market_fig": None})

@app.get("/api/search")
async def search_stocks(q: str = ""):
    """Autocomplete using YFinance."""
    if not q:
        return {"quotes": []}
    try:
        data = yf.Search(q, max_results=10).quotes
        return {"quotes": data}
    except Exception as e:
        return {"error": str(e), "quotes": []}

@app.websocket("/ws/stream-analysis")
async def stream_analysis(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        company = data.get("company")
        if not company:
            await websocket.send_json({"error": "Company ticker is required"})
            await websocket.close()
            return

        graph = build_trading_graph(GROQ_API_KEY)
        
        initial_state = {
            "company_of_interest": company,
            "trade_date": datetime.now().strftime("%Y-%m-%d"),
            "messages": [],
            "investment_debate_state": {"count": 0, "history": ""},
            "risk_debate_state": {"count": 0, "history": ""}
        }

        # Stream Graph Updates
        async for event in graph.astream(initial_state):
            print(f"DEBUG EVENT: {list(event.keys())}")
            for node_name, output in event.items():
                # PREPARE SERIALIZABLE UPDATE
                serializable_update = {}
                for key, value in output.items():
                    if key == "messages":
                        # Convert LangChain messages to simple dicts
                        serializable_update[key] = [
                            {"role": "assistant" if hasattr(m, "content") else "user", "content": getattr(m, "content", str(m))}
                            for m in value
                        ]
                    elif isinstance(value, dict):
                        serializable_update[key] = value
                    else:
                        serializable_update[key] = str(value)

                payload = {
                    "node": node_name,
                    "update": serializable_update,
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_json(payload)
                await asyncio.sleep(0.5)

        await websocket.send_json({"status": "completed"})
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
