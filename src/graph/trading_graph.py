from typing import Annotated, Sequence, TypedDict, Union, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

from src.agents.utils.agent_states import AgentState
from src.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
from src.agents.analysts.market_analyst import create_market_analyst
from src.agents.analysts.news_analyst import create_news_analyst
from src.agents.analysts.operations_analyst import create_operations_analyst
from src.agents.researchers.bull_researcher import create_bull_researcher
from src.agents.researchers.bear_researcher import create_bear_researcher
from src.agents.managers.research_manager import create_research_manager
from src.agents.trader.trader import create_trader
from src.agents.risk_mgmt.risk_agents import create_risk_debator
from src.agents.managers.portfolio_manager import create_portfolio_manager

# Import all tools for the ToolNode
from src.tools.yfinance_tools import get_fundamentals, get_stock_data, get_indicators
from src.tools.scraper_tools import get_bse_xbrl_data, get_exportersindia_data, get_bse_market_context

def build_trading_graph(api_key: str):
    workflow = StateGraph(AgentState)

    # 1. Tools
    tools = [
        get_fundamentals, get_stock_data, get_indicators,
        get_bse_xbrl_data, get_exportersindia_data, get_bse_market_context
    ]
    tool_node = ToolNode(tools)

    # 2. Nodes
    workflow.add_node("fundamentals_analyst", create_fundamentals_analyst(api_key))
    workflow.add_node("market_analyst", create_market_analyst(api_key))
    workflow.add_node("news_analyst", create_news_analyst(api_key))
    workflow.add_node("operations_analyst", create_operations_analyst(api_key))
    workflow.add_node("tools", tool_node)
    
    workflow.add_node("bull_researcher", create_bull_researcher(api_key))
    workflow.add_node("bear_researcher", create_bear_researcher(api_key))
    workflow.add_node("research_manager", create_research_manager(api_key))
    workflow.add_node("trader", create_trader(api_key))
    workflow.add_node("risk_aggressive", create_risk_debator(api_key, "aggressive"))
    workflow.add_node("risk_conservative", create_risk_debator(api_key, "conservative"))
    workflow.add_node("risk_neutral", create_risk_debator(api_key, "neutral"))
    workflow.add_node("portfolio_manager", create_portfolio_manager(api_key))

    # 3. Logic Functions
    def should_continue(state: AgentState):
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return "next"

    def route_after_tool(state: AgentState):
        return state["sender"]

    # 4. Sequential Flow with Tool Support
    # This ensures each analyst finishes their work (including tools) before the next one starts.
    
    workflow.add_edge(START, "fundamentals_analyst")
    workflow.add_conditional_edges("fundamentals_analyst", should_continue, {
        "tools": "tools",
        "next": "market_analyst"
    })
    
    workflow.add_conditional_edges("market_analyst", should_continue, {
        "tools": "tools",
        "next": "operations_analyst"
    })
    
    workflow.add_conditional_edges("operations_analyst", should_continue, {
        "tools": "tools",
        "next": "news_analyst"
    })
    
    # Tool Node Routes back to the agent that called it
    workflow.add_conditional_edges("tools", route_after_tool, {
        "fundamentals_analyst": "fundamentals_analyst",
        "market_analyst": "market_analyst",
        "operations_analyst": "operations_analyst"
    })

    # Linear flow from News Analyst onwards
    workflow.add_edge("news_analyst", "bull_researcher")
    workflow.add_edge("bull_researcher", "bear_researcher")
    workflow.add_edge("bear_researcher", "research_manager")
    workflow.add_edge("research_manager", "trader")
    workflow.add_edge("trader", "risk_aggressive")
    workflow.add_edge("risk_aggressive", "risk_conservative")
    workflow.add_edge("risk_conservative", "risk_neutral")
    workflow.add_edge("risk_neutral", "portfolio_manager")
    workflow.add_edge("portfolio_manager", END)

    return workflow.compile()
