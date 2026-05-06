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

async def run_scrapers_sequentially():
    """Run global scrapers one by one to avoid file renaming collisions."""
    print("STARTUP: Running MarketWatch scraper...")
    await asyncio.to_thread(scrape_bse_500_watchlist)
    await asyncio.sleep(2)
    print("STARTUP: Running Index scraper...")
    await asyncio.to_thread(scrape_bse_industry)
    print("STARTUP: Market data sequence finished.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks."""
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    
    # Always attempt refresh on startup to ensure heatmaps are there
    asyncio.create_task(run_scrapers_sequentially())
    yield

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
             return JSONResponse(content={"error": "data_missing"})

        index_fig, market_fig = await asyncio.to_thread(build_heatmap_figures)
        return JSONResponse(content={
            "index_fig": json.loads(index_fig.to_json()),
            "market_fig": json.loads(market_fig.to_json()),
        })
    except Exception as e:
        print(f"HEATMAP API ERROR: {e}")
        return JSONResponse(content={"error": str(e)})

@app.get("/api/search")
async def search_stocks(q: str = ""):
    if not q: return {"quotes": []}
    try:
        data = yf.Search(q, max_results=8).quotes
        return {"quotes": data}
    except Exception as e: return {"error": str(e), "quotes": []}

@app.websocket("/ws/stream-analysis")
async def stream_analysis(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        raw_company = data.get("company", "")
        # Clean company ticker: strip suffix like .NS and uppercase
        company = raw_company.split(".")[0].upper().strip()
        
        if not company: return await websocket.close()

        graph = build_trading_graph(GROQ_API_KEY)
        initial_state = {
            "company_of_interest": company,
            "trade_date": datetime.now().strftime("%Y-%m-%d"),
            "messages": [],
            "investment_debate_state": {"count": 0, "history": ""},
            "risk_debate_state": {"count": 0, "history": ""}
        }

        async for event in graph.astream(initial_state):
            for node_name, output in event.items():
                # ULTRA-ROBUST SERIALIZATION
                serializable_update = {}
                try:
                    for key, value in output.items():
                        if key == "messages":
                            msgs = []
                            for m in value:
                                # Handle any message type (Human, AI, Tool, System)
                                role = "user"
                                if hasattr(m, "type"):
                                    if m.type == "ai": role = "assistant"
                                    elif m.type == "tool": role = "tool"
                                    elif m.type == "system": role = "system"
                                
                                msgs.append({
                                    "role": role,
                                    "content": str(getattr(m, "content", m)),
                                    "name": getattr(m, "name", node_name)
                                })
                            serializable_update[key] = msgs
                        elif isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                            serializable_update[key] = value
                        else:
                            serializable_update[key] = str(value)

                    await websocket.send_json({
                        "node": node_name,
                        "update": serializable_update,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as ser_err:
                    print(f"SERIALIZATION ERROR in {node_name}: {ser_err}")
                
                await asyncio.sleep(0.1)

        await websocket.send_json({"status": "completed"})
    except WebSocketDisconnect: pass
    except Exception as e:
        print(f"WS GLOBAL ERROR: {e}")
        try: await websocket.send_json({"error": str(e)})
        except: pass
    finally:
        try: await websocket.close()
        except: pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
