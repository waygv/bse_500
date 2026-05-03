from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def create_bear_researcher(api_key: str):
    # Allocation: Qwen model for strong dialectical reasoning in the Bear case
    llm = ChatGroq(
        api_key=api_key,
        model_name="qwen/qwen3-32b",
        temperature=0.8
    )

    def bear_node(state):
        company = state["company_of_interest"]
        investment_debate_state = state.get("investment_debate_state", {})
        history = investment_debate_state.get("history", "")
        
        market_report = state.get("market_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        operations_report = state.get("operations_report", "")
        news_report = state.get("news_report", "")

        prompt = f"""You are a Bear Researcher making the case AGAINST investing in {company}. 
Your goal is to highlight risks, valuation concerns, and negative indicators.
Leverage the following reports:
- Market Report: {market_report}
- Fundamentals Report: {fundamentals_report}
- Operations Report: {operations_report}
- News Report: {news_report}

Conversation history of the debate:
{history}

Focus on financial instability, competitive threats, supply chain vulnerabilities, and macroeconomic headwinds.
Directly challenge the Bull's assumptions with specific data and sound logic.
Be skeptical and thorough.
"""
        response = llm.invoke(prompt)
        argument = f"Bear Researcher: {response.content}"
        
        new_history = history + "\n" + argument
        return {
            "investment_debate_state": {
                **investment_debate_state,
                "history": new_history,
                "bear_history": investment_debate_state.get("bear_history", "") + "\n" + argument,
                "current_response": argument,
                "count": investment_debate_state.get("count", 0) + 1
            }
        }

    return bear_node
