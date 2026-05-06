import json
import os
from datetime import datetime
from typing import Tuple

import pandas as pd
import plotly.express as px

# Get project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def build_heatmap_figures() -> Tuple[px.treemap, px.treemap]:
    """Builds index and market treemap figures with robust error handling."""
    index_path = os.path.join(DATA_PROCESSED_DIR, "Index.csv")
    market_path = os.path.join(DATA_PROCESSED_DIR, "MarketWatch.csv")

    if not os.path.exists(index_path) or not os.path.exists(market_path):
        raise FileNotFoundError(f"CSV files not found at {DATA_PROCESSED_DIR}")

    # --- Load Index Data ---
    index_df = pd.read_csv(index_path)
    index_df.columns = index_df.columns.str.strip()
    
    # Handle numeric columns
    numeric_cols = ["Open", "High", "Low", "Current Value", "Prev. Close", "Ch (pts)", "Ch (%)", "Turnover (Rs. Cr)"]
    for col in numeric_cols:
        if col in index_df.columns:
            index_df[col] = pd.to_numeric(index_df[col].astype(str).str.replace(",", ""), errors="coerce")
    
    index_df = index_df.dropna(subset=["Index", "Current Value", "Turnover (Rs. Cr)"])

    # --- Load Market Data ---
    market_df = pd.read_csv(market_path)
    market_df.columns = market_df.columns.str.strip()

    # Calculate Ch (%) if missing or for accuracy
    market_df["Open"] = pd.to_numeric(market_df["Open"].astype(str).str.replace(",", ""), errors="coerce")
    market_df["LTP"] = pd.to_numeric(market_df["LTP"].astype(str).str.replace(",", ""), errors="coerce")
    market_df["Total Turnover (my image Lac)"] = pd.to_numeric(market_df["Total Turnover (my image Lac)"].astype(str).str.replace(",", ""), errors="coerce")
    
    market_df["Ch (%)"] = ((market_df["LTP"] - market_df["Open"]) / market_df["Open"]) * 100
    market_df = market_df.dropna(subset=["Security Name", "LTP", "Total Turnover (my image Lac)"])

    # ---- INDEX HEATMAP ----
    fig_index = px.treemap(
        index_df,
        path=[px.Constant("BSE Indices"), "Index"],
        values="Turnover (Rs. Cr)",
        color="Ch (%)",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        title="BSE Index Liquidity & Performance",
        hover_data=["Current Value", "Ch (%)", "Turnover (Rs. Cr)"]
    )
    fig_index.update_layout(margin=dict(t=30, l=10, r=10, b=10), paper_bgcolor="#161b22", font_color="#e6edf3")

    # ---- MARKET HEATMAP ----
    fig_market = px.treemap(
        market_df,
        path=[px.Constant("All Stocks"), "Security Group", "Security Name"],
        values="Total Turnover (my image Lac)",
        color="Ch (%)",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        title="Market Snapshot (Turnover vs Performance)",
        hover_data=["LTP", "Ch (%)", "Total Turnover (my image Lac)"]
    )
    fig_market.update_layout(margin=dict(t=30, l=10, r=10, b=10), paper_bgcolor="#161b22", font_color="#e6edf3")

    return fig_index, fig_market

if __name__ == "__main__":
    try:
        f1, f2 = build_heatmap_figures()
        f1.show()
    except Exception as e:
        print(f"Error: {e}")
