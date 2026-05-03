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
            f"Analyze {company}. Use 'get_bse_xbrl_data' to trigger a live Selenium scrape of Indian regulatory filings "
            "if the data is not available or if you need fresh insights. "
            "IMPORTANT: If 'get_bse_xbrl_data' returns an error or is unavailable, DO NOT STOP. "
            "Proceed by relying on 'get_fundamentals' to complete your analysis based on available global financial data. "
            "Acknowledge the missing local data but ensure a comprehensive report is still provided."
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
