from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools.yfinance_tools import get_fundamentals
from src.tools.scraper_tools import get_bse_xbrl_data

def create_fundamentals_analyst(api_key: str):
    llm = ChatGroq(
        api_key=api_key,
        model_name="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.1
    )
    
    tools = [get_fundamentals, get_bse_xbrl_data]
    llm_with_tools = llm.bind_tools(tools)

    def fundamentals_analyst_node(state):
        company = state["company_of_interest"]
        
        system_message = (
            "You are a Senior Fundamentals Analyst. "
            f"Analyze {company}. "
            "IMPORTANT: If you do not have specific Indian regulatory filings (XBRL) in your context, "
            "you MUST call 'get_bse_xbrl_data' to trigger a live Selenium scrape. "
            "If the scraper fails, fall back to 'get_fundamentals' for global financial data. "
            "Always acknowledge the data source in your final report."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt | llm_with_tools
        result = chain.invoke({"messages": state["messages"]})
        
        # If no more tools are called, this is the final report
        report = result.content if not result.tool_calls else ""
        
        return {
            "messages": [result],
            "sender": "fundamentals_analyst",
            "fundamentals_report": report
        }

    return fundamentals_analyst_node
