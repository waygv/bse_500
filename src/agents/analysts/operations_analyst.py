from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools.scraper_tools import get_exportersindia_data

def create_operations_analyst(api_key: str):
    llm = ChatGroq(
        api_key=api_key,
        model_name="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.1
    )
    
    tools = [get_exportersindia_data]
    llm_with_tools = llm.bind_tools(tools)

    def operations_analyst_node(state):
        company = state["company_of_interest"]
        system_message = (
            "You are a Senior Operations Analyst. "
            f"Analyze {company}'s supply chain and business reach. "
            "IMPORTANT: If you do not have current supply chain or export data for this company in your context, "
            "you MUST call 'get_exportersindia_data' to trigger a live Selenium scrape. "
            "Acknowledge any scraper errors, but always provide an operational analysis based "
            "on the data you retrieve or your internal knowledge."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt | llm_with_tools
        result = chain.invoke({"messages": state["messages"]})
        
        # Extract report if final
        report = result.content if not result.tool_calls else ""
        
        return {
            "messages": [result],
            "sender": "operations_analyst",
            "operations_report": report
        }

    return operations_analyst_node
