from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def create_news_analyst(api_key: str):
    # Allocation: Light Context model for news summarization
    llm = ChatGroq(
        api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.1
    )

    def news_analyst_node(state):
        current_date = state.get("trade_date", "Unknown")
        company = state["company_of_interest"]
        
        # In a real app, this would use a news API tool. 
        # For now, it evaluates macro context.
        system_message = (
            "You are a Senior News Analyst. Your task is to analyze recent global and Indian macro-economic news "
            f"that might affect {company}. Look for sector-specific trends, interest rate changes, or regulatory shifts. "
            f"The current date is {current_date}."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("user", f"Analyze news for {company}.")
        ])

        response = llm.invoke(prompt.format_messages())
        
        return {
            "news_report": response.content,
        }

    return news_analyst_node
