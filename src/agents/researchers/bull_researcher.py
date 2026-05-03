from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def create_bull_researcher(api_key: str):
    # Allocation: Qwen model for strong dialectical reasoning in the Bull case
    llm = ChatGroq(
        api_key=api_key,
        model_name="qwen/qwen3-32b",
        temperature=0.8
    )

    def bull_node(state):
        company = state["company_of_interest"]
        investment_debate_state = state.get("investment_debate_state", {})
        history = investment_debate_state.get("history", "")
        
        market_report = state.get("market_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        operations_report = state.get("operations_report", "")
        news_report = state.get("news_report", "")

        prompt = f"""You are a Bull Researcher advocated for investing in {company}. 
Your goal is to build a strong, evidence-based case for why this stock is a BUY.
Leverage the following reports:
- Market Report: {market_report}
- Fundamentals Report: {fundamentals_report}
- Operations Report: {operations_report}
- News Report: {news_report}

Conversation history of the debate:
{history}

Focus on growth potential, competitive advantages (from ExportersIndia), and positive market indicators.
Directly engage with the Bear's points if they have spoken. 
Be persuasive but data-driven.
"""
        response = llm.invoke(prompt)
        argument = f"Bull Researcher: {response.content}"
        
        new_history = history + "\n" + argument
        return {
            "investment_debate_state": {
                **investment_debate_state,
                "history": new_history,
                "bull_history": investment_debate_state.get("bull_history", "") + "\n" + argument,
                "current_response": argument,
                "count": investment_debate_state.get("count", 0) + 1
            }
        }

    return bull_node
