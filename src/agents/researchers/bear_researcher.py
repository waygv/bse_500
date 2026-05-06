from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def create_bear_researcher(api_key: str):
    llm = ChatGroq(
        api_key=api_key,
        model_name="qwen/qwen3-32b",
        temperature=0.7
    )

    def bear_node(state):
        company = state["company_of_interest"]
        investment_debate_state = state.get("investment_debate_state", {})
        history = investment_debate_state.get("history", "")
        
        market_report = state.get("market_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        operations_report = state.get("operations_report", "")
        news_report = state.get("news_report", "")

        prompt = f"""You are a Bear Analyst for {company}. 

ROLE: Present a HIGHLY CONCISE bearish rebuttal.
STRICT RULES:
- USE BULLET POINTS ONLY.
- MAX 5 BULLETS.
- FOCUS ON: Primary risk factor, Valuation concerns, and competitive threats.
- NO PROSE, NO LONG INTROS.

Context:
- Market: {market_report[:1000]}
- Fundamentals: {fundamentals_report[:1000]}
- Operations: {operations_report[:1000]}
- History: {history[-1000:]}

FORMAT:
### BEARISH REBUTTAL
- **Risk 1**: [Short reason]
- **Risk 2**: [Short reason]
...
"""
        response = llm.invoke(prompt)
        argument = f"Bear Researcher: {response.content}"
        
        return {
            "investment_debate_state": {
                **investment_debate_state,
                "history": history + "\n" + argument,
                "bear_history": investment_debate_state.get("bear_history", "") + "\n" + argument,
                "current_response": response.content,
                "count": investment_debate_state.get("count", 0) + 1
            }
        }

    return bear_node
