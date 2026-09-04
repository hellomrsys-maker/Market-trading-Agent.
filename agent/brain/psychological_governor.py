"""
agent/brain/psychological_governor.py
=====================================
OptionAlpha Agent — Disciplined Trader Mental & Psychological Governor
Based on Mark Douglas' "The Disciplined Trader: Developing Winning Attitudes" (New York Institute of Finance)

Core Principles Implemented:
  1. The Market Is Always Right:
     - Prices move in the direction of the greatest net force; personal opinions, hopes, and expectations are subordinate to order flow.
  2. The 2 Master Trading Rules:
     - Rule 1: Predefine exact loss and invalidation reference point on EVERY potential trade before entry.
     - Rule 2: Execute losing trades IMMEDIATELY upon perception without hesitation, rationalization, or hope.
  3. Elimination of Cognitive Biases & Perceptual Distortions:
     - Blocks "Revenge Trading" after losses.
     - Prevents "Windfall Euphoria" and over-sizing after winning streaks.
     - Neutralizes "Loss Avoidance" blind spots (which cause traders to cut winners early and let losers run).
  4. 7 Steps to Flawless Execution:
     - Focus on learning/mastery over money.
     - Total self-acceptance and emotional de-energizing.
     - Thinking in uncommitted probabilities.
     - Objective market observation (detached from personal P&L).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger


@dataclass
class PsychologicalAudit:
    is_disciplined: bool
    state_of_mind: str               # "OBJECTIVE_FLOW" | "EUPHORIA_OVERCONFIDENCE" | "FEAR_AVOIDANCE" | "REVENGE_SEEKING"
    predefined_stop_loss: float
    loss_executed_immediately: bool
    consecutive_wins: int
    consecutive_losses: int
    sizing_penalty_factor: float     # 0.5 to 1.0 (scales down size during emotional tilt)
    guidance_message: str


class PsychologicalGovernor:
    """
    Guards the agent and trader against psychological drift, revenge trading, and loss aversion.
    """

    def __init__(self, max_consecutive_losses: int = 3, max_loss_per_trade_pct: float = 0.02):
        self.max_consecutive_losses = max_consecutive_losses
        self.max_loss_per_trade_pct = max_loss_per_trade_pct
        self._consecutive_wins = 0
        self._consecutive_losses = 0
        self._last_trade_pnl = 0.0

    def record_trade_outcome(self, pnl: float, was_disciplined: bool = True):
        """
        Updates emotional and discipline tracking following trade realization.
        """
        self._last_trade_pnl = pnl
        if pnl > 0:
            self._consecutive_wins += 1
            self._consecutive_losses = 0
        elif pnl < 0:
            self._consecutive_losses += 1
            self._consecutive_wins = 0

    def audit_trade_intent(
        self,
        symbol: str,
        entry_price: float,
        proposed_stop_loss: Optional[float],
        current_equity: float,
        proposed_risk_dollars: float,
    ) -> PsychologicalAudit:
        """
        Audits order intent against Mark Douglas' Disciplined Trader principles.
        """
        # Rule 1 Check: Must predefine loss
        if proposed_stop_loss is None or proposed_stop_loss <= 0.0:
            return PsychologicalAudit(
                is_disciplined=False,
                state_of_mind="FEAR_AVOIDANCE",
                predefined_stop_loss=0.0,
                loss_executed_immediately=False,
                consecutive_wins=self._consecutive_wins,
                consecutive_losses=self._consecutive_losses,
                sizing_penalty_factor=0.0,
                guidance_message="REJECTED: Mark Douglas Rule 1 Violation — Every trade MUST have a predefined loss reference point.",
            )

        # Max Risk Check: Strict 1-2% account limit
        max_allowed_risk = current_equity * self.max_loss_per_trade_pct
        if proposed_risk_dollars > max_allowed_risk * 1.05:
            scale_down = max_allowed_risk / max(1.0, proposed_risk_dollars)
            return PsychologicalAudit(
                is_disciplined=True,
                state_of_mind="OBJECTIVE_FLOW",
                predefined_stop_loss=proposed_stop_loss,
                loss_executed_immediately=True,
                consecutive_wins=self._consecutive_wins,
                consecutive_losses=self._consecutive_losses,
                sizing_penalty_factor=round(scale_down, 3),
                guidance_message=f"ADJUSTED: Proposed risk ${proposed_risk_dollars:.2f} exceeds 2% max risk (${max_allowed_risk:.2f}). Scaled down.",
            )

        # Revenge Trading Check: Consecutive losses tilt protection
        if self._consecutive_losses >= self.max_consecutive_losses:
            return PsychologicalAudit(
                is_disciplined=True,
                state_of_mind="REVENGE_SEEKING",
                predefined_stop_loss=proposed_stop_loss,
                loss_executed_immediately=True,
                consecutive_wins=self._consecutive_wins,
                consecutive_losses=self._consecutive_losses,
                sizing_penalty_factor=0.50, # Cut position size in half during drawdown
                guidance_message="DEFENSIVE: 3+ Consecutive losses detected. Sizing scaled to 50% to prevent revenge trading.",
            )

        # Euphoria Check: 4+ Consecutive wins
        if self._consecutive_wins >= 4:
            return PsychologicalAudit(
                is_disciplined=True,
                state_of_mind="EUPHORIA_OVERCONFIDENCE",
                predefined_stop_loss=proposed_stop_loss,
                loss_executed_immediately=True,
                consecutive_wins=self._consecutive_wins,
                consecutive_losses=self._consecutive_losses,
                sizing_penalty_factor=0.75, # Prevent over-leveraging after hot streaks
                guidance_message="DEFENSIVE: 4+ Consecutive wins. Sizing scaled to 75% to prevent windfall complacency.",
            )

        return PsychologicalAudit(
            is_disciplined=True,
            state_of_mind="OBJECTIVE_FLOW",
            predefined_stop_loss=proposed_stop_loss,
            loss_executed_immediately=True,
            consecutive_wins=self._consecutive_wins,
            consecutive_losses=self._consecutive_losses,
            sizing_penalty_factor=1.0,
            guidance_message="APPROVED: Trade adheres to Disciplined Trader objective probability execution.",
        )
