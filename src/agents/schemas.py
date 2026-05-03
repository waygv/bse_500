from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

# --- Shared rating types ---

class PortfolioRating(str, Enum):
    BUY = "Buy"
    OVERWEIGHT = "Overweight"
    HOLD = "Hold"
    UNDERWEIGHT = "Underweight"
    SELL = "Sell"

class TraderAction(str, Enum):
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"

# --- Research Manager ---

class ResearchPlan(BaseModel):
    recommendation: PortfolioRating = Field(
        description="The investment recommendation. Exactly one of Buy / Overweight / Hold / Underweight / Sell."
    )
    rationale: str = Field(
        description="Summary of the key points from both sides of the debate, ending with which arguments led to the recommendation."
    )
    strategic_actions: str = Field(
        description="Concrete steps for the trader to implement the recommendation."
    )

def render_research_plan(plan: ResearchPlan) -> str:
    return "\n".join([
        f"**Recommendation**: {plan.recommendation.value}",
        "",
        f"**Rationale**: {plan.rationale}",
        "",
        f"**Strategic Actions**: {plan.strategic_actions}",
    ])

# --- Trader ---

class TraderProposal(BaseModel):
    action: TraderAction = Field(description="The transaction direction. Exactly one of Buy / Hold / Sell.")
    reasoning: str = Field(description="The case for this action, anchored in the analysts' reports and the research plan.")
    entry_price: Optional[float] = Field(default=None, description="Optional entry price target.")
    stop_loss: Optional[float] = Field(default=None, description="Optional stop-loss price.")
    position_sizing: Optional[str] = Field(default=None, description="Optional sizing guidance.")

def render_trader_proposal(proposal: TraderProposal) -> str:
    parts = [
        f"**Action**: {proposal.action.value}",
        "",
        f"**Reasoning**: {proposal.reasoning}",
    ]
    if proposal.entry_price is not None:
        parts.extend(["", f"**Entry Price**: {proposal.entry_price}"])
    if proposal.stop_loss is not None:
        parts.extend(["", f"**Stop Loss**: {proposal.stop_loss}"])
    if proposal.position_sizing:
        parts.extend(["", f"**Position Sizing**: {proposal.position_sizing}"])
    parts.extend(["", f"FINAL TRANSACTION PROPOSAL: **{proposal.action.value.upper()}**"])
    return "\n".join(parts)

# --- Portfolio Manager ---

class PortfolioDecision(BaseModel):
    rating: PortfolioRating = Field(description="The final position rating.")
    executive_summary: str = Field(description="A concise action plan covering entry strategy, position sizing, and risk levels.")
    investment_thesis: str = Field(description="Detailed reasoning anchored in specific evidence from the analysts' debate.")
    price_target: Optional[float] = Field(default=None, description="Optional target price.")
    time_horizon: Optional[str] = Field(default=None, description="Optional recommended holding period.")

def render_pm_decision(decision: PortfolioDecision) -> str:
    parts = [
        f"**Rating**: {decision.rating.value}",
        "",
        f"**Executive Summary**: {decision.executive_summary}",
        "",
        f"**Investment Thesis**: {decision.investment_thesis}",
    ]
    if decision.price_target is not None:
        parts.extend(["", f"**Price Target**: {decision.price_target}"])
    if decision.time_horizon:
        parts.extend(["", f"**Time Horizon**: {decision.time_horizon}"])
    return "\n".join(parts)
