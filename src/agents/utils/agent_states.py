from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from langgraph.graph import MessagesState

# Researcher team state (Sub-state)
class InvestDebateState(TypedDict):
    bull_history: Annotated[str, "Bullish Conversation history"]
    bear_history: Annotated[str, "Bearish Conversation history"]
    history: Annotated[str, "Conversation history"]
    current_response: Annotated[str, "Latest response"]
    judge_decision: Annotated[str, "Final judge decision (Research Plan)"]
    count: Annotated[int, "Length of the current conversation"]

# Risk management team state (Sub-state)
class RiskDebateState(TypedDict):
    aggressive_history: Annotated[str, "Aggressive Agent's Conversation history"]
    conservative_history: Annotated[str, "Conservative Agent's Conversation history"]
    neutral_history: Annotated[str, "Neutral Agent's Conversation history"]
    history: Annotated[str, "Conversation history"]
    latest_speaker: Annotated[str, "Analyst that spoke last"]
    current_aggressive_response: Annotated[str, "Latest response by the aggressive analyst"]
    current_conservative_response: Annotated[str, "Latest response by the conservative analyst"]
    current_neutral_response: Annotated[str, "Latest response by the neutral analyst"]
    judge_decision: Annotated[str, "Judge's decision (Final Decision)"]
    count: Annotated[int, "Length of the current conversation"]

# Master State (Global State)
class AgentState(MessagesState):
    company_of_interest: Annotated[str, "Company that we are interested in trading"]
    trade_date: Annotated[str, "What date we are trading at"]
    sender: Annotated[str, "Agent that sent this message"]

    # --- Scraper Data (Indian Market Specific) ---
    raw_xbrl_data: Annotated[Optional[str], "Raw text from BSE XBRL filings"]
    raw_exporters_data: Annotated[Optional[str], "Raw text from ExportersIndia search"]
    bse_market_context: Annotated[Optional[str], "Context from MarketWatch and Index CSVs"]

    # --- Analyst Reports ---
    fundamentals_report: Annotated[str, "Report from the Fundamentals Analyst"]
    sentiment_report: Annotated[str, "Report from the Social Media/Sentiment Analyst"]
    news_report: Annotated[str, "Report from the News Researcher"]
    market_report: Annotated[str, "Report from the Market/Technical Analyst"]
    operations_report: Annotated[str, "Report from the Operations/Supply Chain Analyst"]

    # --- Discussion Steps ---
    investment_debate_state: Annotated[InvestDebateState, "Current state of the Bull/Bear debate"]
    investment_plan: Annotated[str, "Structured Investment Plan from Research Manager"]
    trader_investment_plan: Annotated[str, "Structured Transaction Proposal from Trader"]

    # --- Risk Steps ---
    risk_debate_state: Annotated[RiskDebateState, "Current state of the Risk evaluation debate"]
    final_trade_decision: Annotated[str, "Final Portfolio Decision from Portfolio Manager"]
    
    # --- Context ---
    past_context: Annotated[str, "Memory log context (prior decisions and lessons)"]
