from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools.yfinance_tools import get_stock_data, get_indicators
from src.tools.scraper_tools import get_bse_market_context

def create_market_analyst(api_key: str):
    llm = ChatGroq(
        api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.1
    )
    
    tools = [get_stock_data, get_indicators, get_bse_market_context]
    llm_with_tools = llm.bind_tools(tools)

    def market_analyst_node(state):
        company = state["company_of_interest"]
        
        system_message = (
            "You are a Senior Technical and Market Analyst. "
            f"Your task is to analyze {company}'s market performance and technical indicators. "
            "Use 'get_stock_data' and 'get_indicators' (RSI, MACD) to gauge momentum. "
            "Use 'get_bse_market_context' to see how the stock performs relative to the BSE 500 and its sector. "
            "IMPORTANT: If 'get_bse_market_context' returns an error or is unavailable, DO NOT STOP. "
            "Proceed by relying entirely on 'get_stock_data' and 'get_indicators' to complete your analysis. "
            "Acknowledge the missing local market context but ensure a detailed technical report is still provided."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt | llm_with_tools
        result = chain.invoke({"messages": state["messages"]})
        
        report = result.content if not result.tool_calls else ""
        
        return {
            "messages": [result],
            "sender": "market_analyst",
            "market_report": report
        }

    return market_analyst_node
