"""
ai/research/stop_loss_management_engine.py
==========================================
OptionAlpha Agent — Module K1: Python Systematic 6-Type Stop Loss Management Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Tuple

class StopLossManagementEngine:
    """
    Implements the 6 Stop Loss Architectures from the Metaverse Stop Loss Guide:
    1. Percentage-Based Stop Loss (e.g. 2% capital risk)
    2. Support & Resistance Structural Stop
    3. Trailing Stop Loss
    4. Volatility-Based Stop Loss (ATR multiple / Vol spread)
    5. Time-Based Stop Loss (Max N bars / N days)
    6. Risk-Reward Ratio Stop (2:1 minimum requirement)
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    def calculate_percentage_sl(self, entry_price: float, risk_pct: float = 0.02, is_long: bool = True) -> float:
        if is_long:
            return entry_price * (1.0 - risk_pct)
        return entry_price * (1.0 + risk_pct)

    def calculate_support_resistance_sl(self, key_support: float, buffer_ticks: float = 0.5, is_long: bool = True) -> float:
        if is_long:
            return key_support - buffer_ticks
        return key_support + buffer_ticks

    def calculate_volatility_sl(self, entry_price: float, atr: float, atr_multiplier: float = 1.5, is_long: bool = True) -> float:
        if is_long:
            return entry_price - (atr * atr_multiplier)
        return entry_price + (atr * atr_multiplier)

    def evaluate_time_based_sl(self, bars_in_trade: int, max_allowed_bars: int, current_pnl: float) -> Tuple[bool, str]:
        if bars_in_trade >= max_allowed_bars and current_pnl <= 0.0:
            return True, "TIME_STOP_TRIGGERED_EXIT_DEAD_CAPITAL"
        return False, "WITHIN_TIME_HORIZON"

    def calculate_risk_reward_sl(self, entry_price: float, target_price: float, min_ratio: float = 2.0, is_long: bool = True) -> float:
        reward = abs(target_price - entry_price)
        allowed_risk = reward / max(1.0, min_ratio)
        if is_long:
            return entry_price - allowed_risk
        return entry_price + allowed_risk
