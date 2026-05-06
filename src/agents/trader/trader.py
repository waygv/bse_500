from langchain_groq import ChatGroq
from src.agents.schemas import TraderProposal, render_trader_proposal

def create_trader(api_key: str):
    # Allocation: Versatile model for precise trade instructions
    llm = ChatGroq(
        api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )
    
    structured_llm = llm.with_structured_output(TraderProposal)

    def trader_node(state):
        company = state["company_of_interest"]
        investment_plan = state.get("investment_plan", "")
        
        prompt = f"""You are a Trader turning an investment plan for {company} into a concrete transaction proposal.
Investment Plan:
{investment_plan}

Decide on the action (Buy, Hold, or Sell).
Define entry price, stop loss, and position sizing guidance.
Ground your reasoning in the provided plan.
"""
        
        try:
            proposal = structured_llm.invoke(prompt)
            rendered_proposal = render_trader_proposal(proposal)
        except Exception as e:
            response = llm.invoke(prompt)
            rendered_proposal = response.content

        return {
            "trader_investment_plan": rendered_proposal,
        }

    return trader_node
