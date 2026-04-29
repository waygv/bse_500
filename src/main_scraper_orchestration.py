import json
import os
import subprocess
import sys
from datetime import datetime
import logging
from typing import List, Dict, Any

# === HARDCODED COMPANY NAME ===
TARGET_COMPANY = "CIPLA"  # <--- CHANGE THIS TO YOUR TARGET COMPANY

# Get the directory where THIS script is located (src/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project root (one level up from src/)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# === Scripts to run (base stack) ===
SCRIPTS_CONFIG = [
    {"name": os.path.join(SCRIPT_DIR, "scrapers", "bse_500_watchlist.py"), "args": []},
    {"name": os.path.join(SCRIPT_DIR, "scrapers", "bse_industry.py"), "args": []},
    {"name": os.path.join(SCRIPT_DIR, "analysis", "heatmap.py"), "args": []},
]

# Specifically for company-wise scraping
COMPANY_SCRIPTS = [
    {"name": os.path.join(SCRIPT_DIR, "scrapers", "bse_companywise.py"), "args": [TARGET_COMPANY]},
    {"name": os.path.join(SCRIPT_DIR, "scrapers", "exportersindia_dom_scraper.py"), "args": [TARGET_COMPANY]},
]

# === Logging setup ===
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "scraper_orchestration.log")

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

def run_script(script_path: str, args: List[str]):
    """Run a Python script as subprocess with error handling."""
    command = [sys.executable, script_path] + args
    logging.info(f"START: Running {os.path.basename(script_path)} with args: {args}")

    try:
        if not os.path.exists(script_path):
            logging.error(f"ERROR: {script_path} not found")
            return

        result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT_DIR)

        if result.returncode == 0:
            logging.info(f"SUCCESS: {os.path.basename(script_path)} completed successfully")
        else:
            logging.error(f"FAILURE: {os.path.basename(script_path)} failed with code {result.returncode}")
            if result.stderr.strip():
                logging.error(f"STDERR:\n{result.stderr.strip()}")

    except Exception as e:
        logging.exception(f"EXCEPTION: Error running {script_path}: {e}")

def run_all(company: str = TARGET_COMPANY):
    """Run all configured scripts."""
    start_time = datetime.now()
    logging.info("=== SCRAPER ORCHESTRATION STARTED ===")
    logging.info(f"Target company: {company}")

    for config in SCRIPTS_CONFIG:
        run_script(config["name"], config["args"])
        logging.info("-" * 40)

    for config in COMPANY_SCRIPTS:
        run_script(config["name"], [company])
        logging.info("-" * 40)

    end_time = datetime.now()
    logging.info(f"=== ALL SCRIPTS COMPLETED IN {end_time - start_time} ===")
    logging.info(f"Logs saved to: {LOG_FILE}")

if __name__ == "__main__":
    run_all()
