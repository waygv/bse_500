import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.analysis.heatmap import build_heatmap_figures
from src.analysis.llm_parser_gemini import process_single_company
from src.main_scraper_orchestration import run_all, SCRIPTS_CONFIG, TARGET_COMPANY

DEBUG_LOG_PATH = r"c:\Users\vinay\OneDrive\Desktop\core\bse_500\.cursor\debug.log"
SESSION_ID = "debug-session"

app = FastAPI(title="BSE 500 Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")


def _agent_log(hypothesis_id: str, location: str, message: str, data: Dict[str, Any]):
    payload = {
        "sessionId": SESSION_ID,
        "runId": "prefill",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.utcnow().timestamp() * 1000),
    }
    try:
        # region agent log
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _log:
            _log.write(json.dumps(payload) + "\n")
        # endregion
    except Exception:
        pass


@app.get("/")
async def serve_index():
    _agent_log("H1", "app.py:serve_index", "serve_index", {})
    return FileResponse("static/index.html")


@app.get("/api/heatmap")
async def heatmap_data():
    _agent_log("H2", "app.py:heatmap_data", "start", {})
    try:
        index_fig, market_fig = await asyncio.to_thread(build_heatmap_figures)
        payload = {
            "index_fig": json.loads(index_fig.to_json()),
            "market_fig": json.loads(market_fig.to_json()),
        }
        _agent_log("H2", "app.py:heatmap_data", "success", {"index_nodes": len(payload["index_fig"].get("data", [])), "market_nodes": len(payload["market_fig"].get("data", []))})
        return JSONResponse(content=payload)
    except Exception as e:
        _agent_log("H2", "app.py:heatmap_data", "error", {"error": str(e)})
        raise


def _build_script_plan(company: Optional[str]) -> List[Dict[str, Any]]:
    config = []
    if company:
        config.extend(
            [
                {"name": "src/scrapers/bse_companywise.py", "args": [company]},
                {"name": "src/scrapers/exportersindia_dom_scraper.py", "args": [company]},
            ]
        )
    config.extend(SCRIPTS_CONFIG)
    return config


@app.post("/api/run-scrapers")
async def run_scrapers(background_tasks: BackgroundTasks, company: Optional[str] = None):
    run_id = f"api-{int(time.time())}"
    scripts_plan = _build_script_plan(company or TARGET_COMPANY)
    _agent_log("H1", "app.py:run_scrapers", "start", {"runId": run_id, "company": company or TARGET_COMPANY, "scripts": [c['name'] for c in scripts_plan]})
    background_tasks.add_task(run_all, scripts_plan, run_id)
    return {"status": "started", "runId": run_id, "scripts": [c["name"] for c in scripts_plan]}


@app.get("/api/analysis")
async def company_analysis(company: str):
    if not company:
        raise HTTPException(status_code=400, detail="company is required")
    run_id = f"analysis-{int(time.time())}"
    _agent_log("H4", "app.py:company_analysis", "start", {"company": company, "runId": run_id})
    try:
        result = await asyncio.to_thread(process_single_company, company, run_id)
        _agent_log("H4", "app.py:company_analysis", "success", {"company": company})
        return {"company": company, "analysis": result}
    except Exception as e:
        _agent_log("H4", "app.py:company_analysis", "error", {"company": company, "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
