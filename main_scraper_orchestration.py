import json
import os
import subprocess
import sys
from datetime import datetime
import logging
from typing import List, Dict, Any

# === Hardcoded company name ===
TARGET_COMPANY = "CIPLA"

# === Scripts to run (base stack) ===
SCRIPTS_CONFIG = [
    {"name": "bse_500_watchlist.py", "args": []},
    {"name": "bse_industry.py", "args": []},
    {"name": "heatmap.py", "args": []},
]

# === Logging setup (existing run log) ===
LOG_FILE = "scraper_orchestration.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(console_handler)

# === Debug-mode NDJSON log path ===
DEBUG_LOG_PATH = r"c:\Users\vinay\OneDrive\Desktop\core\bse_500\.cursor\debug.log"
SESSION_ID = "debug-session"


def _agent_log(hypothesis_id: str, location: str, message: str, data: Dict[str, Any]):
    """Append a single NDJSON log line for debug mode instrumentation."""
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
        # Avoid breaking main flow if debug logging fails
        pass


def run_script(script_name: str, args: List[str]):
    """Run a Python script as subprocess with error handling."""
    command = [sys.executable, script_name] + args
    logging.info(f"🚀 Starting {script_name} with args: {args}")
    _agent_log("H1", "main_scraper_orchestration.py:run_script", "start_script", {"script": script_name, "args": args})

    try:
        if not os.path.exists(script_name):
            logging.error(f"❌ {script_name} not found")
            _agent_log("H1", "main_scraper_orchestration.py:run_script", "script_missing", {"script": script_name})
            return

        result = subprocess.run(command, capture_output=True, text=True)
        _agent_log(
            "H1",
            "main_scraper_orchestration.py:run_script",
            "script_completed",
            {"script": script_name, "code": result.returncode, "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]},
        )

        if result.returncode == 0:
            logging.info(f"✅ {script_name} completed successfully")
            if result.stdout.strip():
                logging.debug(f"Output:\n{result.stdout.strip()}")
        else:
            logging.error(f"❌ {script_name} failed with code {result.returncode}")
            if result.stderr.strip():
                logging.error(f"STDERR:\n{result.stderr.strip()}")
            if result.stdout.strip():
                logging.error(f"STDOUT:\n{result.stdout.strip()}")

    except Exception as e:
        logging.exception(f"⚠️ Exception running {script_name}: {e}")
        _agent_log("H1", "main_scraper_orchestration.py:run_script", "exception", {"script": script_name, "error": str(e)})


def run_all(scripts_config: List[Dict[str, Any]] = None, run_id: str = "manual"):
    """Run all configured scripts; kept callable by API."""
    effective_config = scripts_config or SCRIPTS_CONFIG
    start_time = datetime.now()
    logging.info("=== 🧭 Scraper Orchestration Started ===")
    logging.info(f"Target company: {TARGET_COMPANY}")
    _agent_log("H2", "main_scraper_orchestration.py:run_all", "orchestration_start", {"runId": run_id, "count": len(effective_config)})

    for config in effective_config:
        run_script(config["name"], config["args"])
        logging.info("-" * 80)

    end_time = datetime.now()
    logging.info(f"=== ✅ All scripts completed in {end_time - start_time} ===")
    logging.info(f"Logs saved to: {os.path.abspath(LOG_FILE)}")
    _agent_log("H2", "main_scraper_orchestration.py:run_all", "orchestration_end", {"runId": run_id, "duration_sec": (end_time - start_time).total_seconds()})


def main():
    run_all()


if __name__ == "__main__":
    main()