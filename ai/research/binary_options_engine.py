"""
ai/research/binary_options_engine.py
====================================
OptionAlpha Agent — Module S1: Python Binary Digital & Volatility Strangle Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple

class BinaryOptionsEngine:
    """
    Synthesizes 'Binary Options: Strategies for Directional and Volatility Trading' (Alex Nekritin):
    - All-or-nothing $0 / $100 payout mechanics & 100% full collateralization
    - Volatility Long (Strangle: Long OTM High + Short OTM Low)
    - Volatility Short (Premium Collection: Short OTM High + Long ITM Low)
    - Loss Cutoff Multiplier Rule (1:3 - 1:6) & Break-Even Compensation
    - Strike Distance Optimization for Mean-Reverting Indices (>= 2.5-3.0% buffer)
    - Staggered Weekly Legging Strategy (Monday/Tuesday accumulation)
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    @staticmethod
    def calculate_collateral_and_payout(
        trade_type: str, # "LONG" or "SHORT"
        premium: float,
        contracts: int = 1
    ) -> Dict[str, float]:
        """
        Collateral & Max Payout:
        Long Trade: Collateral = Premium * N, Max Profit = ($100 - Premium) * N
        Short Trade: Collateral = ($100 - Premium) * N, Max Profit = Premium * N
        """
        if trade_type == "LONG":
            collateral_per_contract = premium
            max_profit_per_contract = 100.0 - premium
        else: # "SHORT"
            collateral_per_contract = 100.0 - premium
            max_profit_per_contract = premium

        total_collateral = collateral_per_contract * contracts
        total_max_profit = max_profit_per_contract * contracts
        reward_risk_ratio = total_max_profit / max(1e-4, total_collateral)

        return {
            "trade_type": trade_type,
            "collateral_per_contract": collateral_per_contract,
            "max_profit_per_contract": max_profit_per_contract,
            "total_collateral": total_collateral,
            "total_max_profit": total_max_profit,
            "reward_risk_ratio": reward_risk_ratio
        }

    @staticmethod
    def evaluate_volatility_strangle(
        is_long_volatility: bool,
        high_strike_ask: float,
        low_strike_bid: float,
        contracts: int = 1
    ) -> Dict[str, float]:
        """
        Volatility Long: Buy OTM High + Sell OTM Low
        - Total Collateral = (High Ask + ($100 - Low Bid)) * N
        - Max Profit = $100 * N - Total Collateral

        Volatility Short (Premium Collection): Sell OTM High + Buy ITM Low
        - Total Collateral = (Low Ask + ($100 - High Bid)) * N
        - Max Profit = $200 * N - Total Collateral (if held between strikes)
        - Max Loss (Single Breach) = Max Loss on breached leg - Gain on preserved leg
        """
        if is_long_volatility:
            long_collateral = high_strike_ask
            short_collateral = 100.0 - low_strike_bid
            total_collateral = (long_collateral + short_collateral) * contracts
            max_profit = (100.0 * contracts) - total_collateral
            max_loss = total_collateral
            rr_ratio = max_profit / max(1e-4, max_loss)
        else:
            long_leg_cost = low_strike_bid # buying lower ITM
            short_leg_collateral = 100.0 - high_strike_ask # selling upper OTM
            total_collateral = (long_leg_cost + short_leg_collateral) * contracts
            max_profit = (200.0 * contracts) - total_collateral
            # Higher of upper or lower breach loss
            upper_loss = short_leg_collateral - (100.0 - long_leg_cost)
            lower_loss = long_leg_cost - (100.0 - short_leg_collateral)
            max_loss = max(abs(upper_loss), abs(lower_loss)) * contracts
            rr_ratio = max_profit / max(1e-4, max_loss)

        return {
            "strategy": "LONG_STRANGLE_VOLATILITY" if is_long_volatility else "SHORT_STRANGLE_PREMIUM_COLLECTION",
            "total_collateral": total_collateral,
            "max_profit": max_profit,
            "max_loss": max_loss,
            "reward_risk_ratio": rr_ratio
        }

    @staticmethod
    def calculate_cutoff_thresholds(
        premium_collected: float,
        target_risk_multiple: float = 3.0
    ) -> Dict[str, float]:
        """
        Calculates proactive loss cutoffs for short volatility spreads (e.g. 1:3 to 1:6 rule)
        to prevent single tail events from erasing accumulated wins.
        """
        max_allowable_loss = premium_collected * target_risk_multiple
        exit_option_threshold_bid = 100.0 - max_allowable_loss
        
        return {
            "premium_collected": premium_collected,
            "risk_multiple": target_risk_multiple,
            "max_allowable_loss": max_allowable_loss,
            "cutoff_trigger_loss": max_allowable_loss
        }
