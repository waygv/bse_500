from langchain_groq import ChatGroq

def create_risk_debator(api_key: str, stance: str):
    # Allocation: GPT-OSS-20B for risk diversification
    llm = ChatGroq(
        api_key=api_key,
        model_name="openai/gpt-oss-20b",
        temperature=0.7
    )

    def risk_node(state):
        company = state["company_of_interest"]
        trader_plan = state.get("trader_investment_plan", "")
        risk_state = state.get("risk_debate_state", {})
        history = risk_state.get("history", "")
        
        market_report = state.get("market_report", "")
        
        system_prompts = {
            "aggressive": "You are an Aggressive Risk Analyst. You champion high-reward opportunities and believe in bold scaling when momentum is strong.",
            "conservative": "You are a Conservative Risk Analyst. Your priority is asset protection and minimizing volatility. You highlight every potential pitfall.",
            "neutral": "You are a Neutral Risk Analyst. You provide a balanced view, weighing the aggressive and conservative stances against market liquidity."
        }

        prompt = f"""{system_prompts[stance]} 
Evaluate the following trade proposal for {company}:
{trader_plan}

Consider the Market Context:
{market_report}

Current Debate History:
{history}

Argue your stance clearly. Respond to previous debaters if applicable.
"""
        response = llm.invoke(prompt)
        argument = f"{stance.capitalize()} Analyst: {response.content}"
        
        new_history = history + "\n" + argument
        
        # Update the specific stance history
        stance_key = f"{stance}_history"
        
        return {
            "risk_debate_state": {
                **risk_state,
                "history": new_history,
                stance_key: risk_state.get(stance_key, "") + "\n" + argument,
                "latest_speaker": stance.capitalize(),
                "count": risk_state.get("count", 0) + 1
            }
        }

    return risk_node
