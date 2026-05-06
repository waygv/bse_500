from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def create_bull_researcher(api_key: str):
    llm = ChatGroq(
        api_key=api_key,
        model_name="qwen/qwen3-32b",
        temperature=0.7
    )

    def bull_node(state):
        company = state["company_of_interest"]
        investment_debate_state = state.get("investment_debate_state", {})
        history = investment_debate_state.get("history", "")
        
        market_report = state.get("market_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        operations_report = state.get("operations_report", "")
        news_report = state.get("news_report", "")

        prompt = f"""You are a Bull Analyst for {company}. 

ROLE: Present a HIGHLY CONCISE bullish thesis.
STRICT RULES:
- USE BULLET POINTS ONLY.
- MAX 5 BULLETS.
- FOCUS ON: Strongest growth driver, Financial stability, and Operational reach.
- NO PROSE, NO LONG INTROS.

Context:
- Market: {market_report[:1000]}
- Fundamentals: {fundamentals_report[:1000]}
- Operations: {operations_report[:1000]}
- History: {history[-1000:]}

FORMAT:
### BULLISH THESIS
- **Point 1**: [Short reason]
- **Point 2**: [Short reason]
...
"""
        response = llm.invoke(prompt)
        argument = f"Bull Researcher: {response.content}"
        
        return {
            "investment_debate_state": {
                **investment_debate_state,
                "history": history + "\n" + argument,
                "bull_history": investment_debate_state.get("bull_history", "") + "\n" + argument,
                "current_response": response.content,
                "count": investment_debate_state.get("count", 0) + 1
            }
        }

    return bull_node
