from langchain_groq import ChatGroq
from src.agents.schemas import PortfolioDecision, render_pm_decision

def create_portfolio_manager(api_key: str):
    # Allocation: Versatile model for the final decision and structured output
    llm = ChatGroq(
        api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )
    
    structured_llm = llm.with_structured_output(PortfolioDecision)

    def portfolio_manager_node(state):
        company = state["company_of_interest"]
        research_plan = state.get("investment_plan", "")
        trader_plan = state.get("trader_investment_plan", "")
        risk_history = state.get("risk_debate_state", {}).get("history", "")
        
        prompt = f"""As the Portfolio Manager for our Indian Trading Desk, your task is to synthesize the research, 
the trade proposal, and the risk analysts' debate to deliver the final decision for {company}.

Research Plan:
{research_plan}

Trader's Proposal:
{trader_plan}

Risk Analysts Debate:
{risk_history}

Provide a final rating (Buy, Overweight, Hold, Underweight, or Sell).
Write an executive summary and a detailed investment thesis.
Include price targets and time horizons if applicable.
"""
        
        try:
            decision = structured_llm.invoke(prompt)
            rendered_decision = render_pm_decision(decision)
        except Exception as e:
            response = llm.invoke(prompt)
            rendered_decision = response.content

        return {
            "final_trade_decision": rendered_decision,
        }

    return portfolio_manager_node
