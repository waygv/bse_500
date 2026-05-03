import os
import pandas as pd
from langchain_core.tools import tool
from typing import Annotated

# Import the scraper functions
from src.scrapers.bse_companywise import scrape_bse_xbrl
from src.scrapers.exportersindia_dom_scraper import scrape_exportersindia
from src.scrapers.bse_500_watchlist import scrape_bse_500_watchlist
from src.scrapers.bse_industry import scrape_bse_industry

# Get project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

@tool
def get_bse_xbrl_data(
    symbol: Annotated[str, "Ticker symbol of the company"],
    force_refresh: Annotated[bool, "Whether to force a new scrape"] = False
) -> str:
    """Read existing BSE XBRL text data. If file is missing, it triggers a live Selenium scrape."""
    filepath = os.path.join(DATA_RAW_DIR, f"{symbol.upper()}_xbrl.txt")
    
    if force_refresh or not os.path.exists(filepath):
        print(f"DEBUG: Triggering live BSE scrape for {symbol}...")
        result = scrape_bse_xbrl(symbol)
        if "ERROR" in result:
            return result

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading XBRL data for {symbol}: {str(e)}"

@tool
def get_exportersindia_data(
    symbol: Annotated[str, "Ticker symbol of the company"],
    force_refresh: Annotated[bool, "Whether to force a new scrape"] = False
) -> str:
    """Read existing ExportersIndia text data. If file is missing, it triggers a live Selenium scrape."""
    filepath = os.path.join(DATA_RAW_DIR, f"{symbol.upper()}_exportersindia.txt")
    
    if force_refresh or not os.path.exists(filepath):
        print(f"DEBUG: Triggering live ExportersIndia scrape for {symbol}...")
        result = scrape_exportersindia(symbol)
        if "ERROR" in result:
            return result

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading ExportersIndia data for {symbol}: {str(e)}"

@tool
def get_bse_market_context(
    symbol: Annotated[str, "Ticker symbol of the company"]
) -> str:
    """Get the company's performance context. If MarketWatch.csv or Index.csv are missing, triggers a download."""
    marketwatch_path = os.path.join(DATA_PROCESSED_DIR, "MarketWatch.csv")
    index_path = os.path.join(DATA_PROCESSED_DIR, "Index.csv")
    
    # Trigger download if missing
    if not os.path.exists(marketwatch_path):
        print("DEBUG: MarketWatch.csv missing. Downloading...")
        scrape_bse_500_watchlist()
        
    if not os.path.exists(index_path):
        print("DEBUG: Index.csv missing. Downloading...")
        scrape_bse_industry()

    context = ""
    
    if os.path.exists(marketwatch_path):
        try:
            df = pd.read_csv(marketwatch_path)
            df.columns = df.columns.str.strip()
            match = df[df["Security Name"].str.upper().str.contains(symbol.upper(), na=False)]
            if not match.empty:
                context += f"MarketWatch Data for {symbol}:\n{match.to_string(index=False)}\n\n"
        except Exception as e:
            context += f"Error reading MarketWatch.csv: {str(e)}\n\n"
            
    if os.path.exists(index_path):
        try:
            df_idx = pd.read_csv(index_path)
            df_idx.columns = df_idx.columns.str.strip()
            context += f"Overall BSE Index Performance:\n{df_idx.to_string(index=False)}"
        except Exception as e:
            context += f"Error reading Index.csv: {str(e)}\n"
            
    return context if context else "Failed to retrieve market context."
