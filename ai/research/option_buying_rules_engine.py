"""
ai/research/option_buying_rules_engine.py
=========================================
OptionAlpha Agent — Module J1: Python Option Buyer's Volatility & Milestone Trailing Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Tuple

class OptionBuyingRulesEngine:
    """
    Implements Metaverse Rules & Tricks for Option Buyers:
    - ITM Strike Selection & Gamma leverage vs. Theta decay
    - VIX Volatility Filter (Buy during low VIX, hedge/avoid high VIX decay)
    - Cash/Futures Level Trigger (Execute option only when underlying triggers)
    - Multi-target milestone trailing stop (T1 hit -> SL to Cost, T2 hit -> SL to T1)
    - Strict holding window (Intraday to 3 days max)
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    def validate_option_buying_setup(
        self,
        is_trending: bool,
        is_consolidation: bool,
        vix_level: float,
        underlying_price: float,
        cash_trigger_level: float,
        holding_days: int
    ) -> Dict[str, bool | str]:
        if is_consolidation:
            return {
                "allow_entry": False,
                "reason": "REJECTED_CONSOLIDATION_KILLS_OPTION_BUYERS_THETA_DECAY"
            }
        if holding_days > 3:
            return {
                "allow_entry": False,
                "reason": "REJECTED_EXCEEDS_MAX_3_DAY_HOLDING_WINDOW"
            }
        if not is_trending:
            return {
                "allow_entry": False,
                "reason": "REJECTED_NO_CLEAR_TREND_OR_BREAKOUT"
            }
        
        # Volatility condition: low/rising VIX favored for option buying
        vix_favorable = vix_level < 22.0
        trigger_active = underlying_price >= cash_trigger_level

        return {
            "allow_entry": trigger_active and vix_favorable,
            "vix_regime": "FAVORABLE_LOW_VIX" if vix_favorable else "HIGH_VIX_EXPENSIVE_PREMIUMS",
            "trigger_met": trigger_active,
            "reason": "APPROVED_OPTIMAL_OPTION_BUYING_MOMENTUM" if (trigger_active and vix_favorable) else "AWAITING_CASH_TRIGGER"
        }

    def update_milestone_trailing_stop(
        self,
        entry_premium: float,
        current_premium: float,
        target_1: float,
        target_2: float,
        target_3: float,
        initial_sl: float
    ) -> Tuple[float, str]:
        """
        Milestone-based stop management:
        - Before T1: SL is initial SL
        - After reaching T1: SL moves to entry cost (Cost / Breakeven)
        - After reaching T2: SL moves to Target 1
        - After reaching T3: SL moves to Target 2
        """
        if current_premium >= target_3:
            return target_2, "TRAILING_AT_TARGET_2"
        elif current_premium >= target_2:
            return target_1, "TRAILING_AT_TARGET_1"
        elif current_premium >= target_1:
            return entry_premium, "TRAILING_AT_COST_BREAKEVEN"
        return initial_sl, "INITIAL_PROTECTIVE_STOP"
