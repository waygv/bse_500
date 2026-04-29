import json
from datetime import datetime
from typing import Tuple

import pandas as pd
import plotly.express as px

DEBUG_LOG_PATH = r"c:\Users\vinay\OneDrive\Desktop\core\bse_500\.cursor\debug.log"
SESSION_ID = "debug-session"


def _agent_log(hypothesis_id: str, location: str, message: str, data):
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


def build_heatmap_figures() -> Tuple[px.treemap, px.treemap]:
    """Builds index and market treemap figures."""
    index_df = pd.read_csv("data/processed/Index.csv")
    index_df.columns = index_df.columns.str.strip()
    market_df = pd.read_csv("data/processed/MarketWatch.csv")
    market_df.columns = market_df.columns.str.strip()

    # Convert numeric columns safely
    for col in index_df.columns[1:]:
        index_df[col] = pd.to_numeric(index_df[col].astype(str).str.replace(",", ""), errors="coerce")

    for col in market_df.columns[3:]:
        market_df[col] = pd.to_numeric(market_df[col].astype(str).str.replace(",", ""), errors="coerce")

    # Calculate stock % change
    market_df["Ch (%)"] = ((market_df["LTP"] - market_df["Open"]) / market_df["Open"]) * 100

    # ---- INDEX HEATMAP (Treemap) ----
    fig_index = px.treemap(
        index_df,
        path=["Index"],
        values="Turnover (Rs. Cr)",  # Size = liquidity
        color="Ch (%)",  # Color = performance
        hover_data=index_df.columns,
        color_continuous_scale="RdYlGn",
        title="Index Heatmap (Performance vs Liquidity)",
    )

    # ---- MARKET HEATMAP (Treemap) ----
    fig_market = px.treemap(
        market_df,
        path=["Security Group", "Security Name"],
        values="Total Turnover (my image Lac)",  # Size = liquidity
        color="Ch (%)",  # Color = performance
        hover_data=market_df.columns,
        color_continuous_scale="RdYlGn",
        title="Market Heatmap (Stock Performance vs Turnover)",
    )
    _agent_log("H2", "heatmap.py:build_heatmap_figures", "heatmap_built", {"index_rows": len(index_df), "market_rows": len(market_df)})
    return fig_index, fig_market


def main():
    fig_index, fig_market = build_heatmap_figures()
    fig_index.show()
    fig_market.show()


if __name__ == "__main__":
    main()
