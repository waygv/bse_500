from langchain_groq import ChatGroq
from src.agents.schemas import ResearchPlan, render_research_plan

def create_research_manager(api_key: str):
    # Allocation: Versatile model for final synthesis and structured output
    llm = ChatGroq(
        api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )
    
    structured_llm = llm.with_structured_output(ResearchPlan)

    def research_manager_node(state):
        company = state["company_of_interest"]
        history = state.get("investment_debate_state", {}).get("history", "")
        
        prompt = f"""As the Research Manager, your role is to critically evaluate the Bull vs. Bear debate for {company} 
and deliver a clear, actionable investment plan.

Debate History:
{history}

Based on the strongest arguments presented, decide on a recommendation (Buy, Overweight, Hold, Underweight, or Sell).
Provide a detailed rationale and strategic actions for the trader.
Commit to a clear stance; only recommend 'Hold' if the evidence is truly balanced.
"""
        
        try:
            plan = structured_llm.invoke(prompt)
            rendered_plan = render_research_plan(plan)
        except Exception as e:
            # Fallback to free text if structured output fails
            response = llm.invoke(prompt)
            rendered_plan = response.content

        return {
            "investment_plan": rendered_plan,
        }

    return research_manager_node
