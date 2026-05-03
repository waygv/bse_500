import yfinance as yf
import pandas as pd
from langchain_core.tools import tool
from typing import Annotated

@tool
def get_stock_data(
    symbol: Annotated[str, "Ticker symbol of the company"],
    period: Annotated[str, "Period to fetch data for (e.g., '1mo', '3mo', '1y')"] = "1mo"
) -> str:
    """Retrieve historical stock price data (OHLCV) for a given ticker symbol."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            return f"No stock data found for {symbol}."
        return df.to_string()
    except Exception as e:
        return f"Error fetching stock data for {symbol}: {str(e)}"

@tool
def get_fundamentals(
    symbol: Annotated[str, "Ticker symbol of the company"]
) -> str:
    """Retrieve fundamental data (balance sheet, income statement, cash flow) for a given ticker symbol."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get key metrics
        summary = {
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Market Cap": info.get("marketCap"),
            "PE Ratio": info.get("trailingPE"),
            "EPS": info.get("trailingEps"),
            "Revenue Growth": info.get("revenueGrowth"),
            "Profit Margin": info.get("profitMargins"),
        }
        
        income_stmt = ticker.income_stmt
        balance_sheet = ticker.balance_sheet
        
        report = f"Summary Metrics for {symbol}:\n{summary}\n\n"
        report += f"Income Statement (Latest):\n{income_stmt.iloc[:, 0:2].to_string()}\n\n"
        report += f"Balance Sheet (Latest):\n{balance_sheet.iloc[:, 0:2].to_string()}"
        
        return report
    except Exception as e:
        return f"Error fetching fundamentals for {symbol}: {str(e)}"

@tool
def get_indicators(
    symbol: Annotated[str, "Ticker symbol of the company"],
    indicators: Annotated[str, "Comma-separated list of indicators (e.g., 'rsi,macd,sma50')"] = "rsi,macd"
) -> str:
    """Calculate technical indicators like RSI, MACD, and SMAs for a given ticker."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")
        if df.empty:
            return f"No stock data found for {symbol} to calculate indicators."
        
        results = {}
        requested = [i.strip().lower() for i in indicators.split(",")]
        
        # Simple RSI calculation
        if "rsi" in requested:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            results["Current RSI"] = df['RSI'].iloc[-1]
            
        # Simple MACD
        if "macd" in requested:
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            results["MACD"] = df['MACD'].iloc[-1]
            results["MACD Signal"] = df['Signal'].iloc[-1]
            
        if "sma50" in requested:
            results["SMA 50"] = df['Close'].rolling(window=50).mean().iloc[-1]
            
        return str(results)
    except Exception as e:
        return f"Error calculating indicators for {symbol}: {str(e)}"
