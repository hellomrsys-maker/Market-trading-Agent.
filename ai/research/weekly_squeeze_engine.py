"""
ai/research/weekly_squeeze_engine.py
====================================
OptionAlpha Agent — Module Q1: Python Dynamic Weekly Squeeze & Heikin Ashi Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple

class WeeklySqueezeEngine:
    """
    Synthesizes 'Dynamic Trading with Weekly Options' (Haddock & Kapoor):
    - Heikin Ashi smoothing (Open, High, Low, Close)
    - TTM Squeeze (Bollinger Bands vs Keltner Channels) & 13/21/55 EMA Ribbon
    - 2-Bar Confirmation & 50% Midpoint Retracement Entry
    - Dynamic Weekly Spread Legging: Directional Credit Spread -> Iron Condor
    - Market Maker Expected Move (MMM) & Pre-Earnings Volatility Crush
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    @staticmethod
    def calculate_heikin_ashi(
        open_p: float, high_p: float, low_p: float, close_p: float,
        prev_ha_open: float, prev_ha_close: float
    ) -> Dict[str, float]:
        """
        HA Formula:
        Open = (prev_ha_open + prev_ha_close) / 2
        Close = (open + high + low + close) / 4
        High = max(high, Open, Close)
        Low = min(low, Open, Close)
        """
        ha_open = (prev_ha_open + prev_ha_close) / 2.0
        ha_close = (open_p + high_p + low_p + close_p) / 4.0
        ha_high = max(high_p, ha_open, ha_close)
        ha_low = min(low_p, ha_open, ha_close)
        
        # Bullish: ha_close > ha_open, no lower tail (ha_low == ha_open)
        # Bearish: ha_close < ha_open, no upper wick (ha_high == ha_open)
        is_strong_bull = (ha_close > ha_open) and (abs(ha_low - ha_open) < 1e-4)
        is_strong_bear = (ha_close < ha_open) and (abs(ha_high - ha_open) < 1e-4)
        
        return {
            "ha_open": ha_open,
            "ha_high": ha_high,
            "ha_low": ha_low,
            "ha_close": ha_close,
            "is_strong_bull": is_strong_bull,
            "is_strong_bear": is_strong_bear,
            "signal_color": "WHITE" if ha_close >= ha_open else "RED"
        }

    @staticmethod
    def detect_ttm_squeeze(
        bb_upper: float, bb_lower: float,
        keltner_upper: float, keltner_lower: float,
        ema13: float, ema21: float, ema55: float
    ) -> Dict[str, bool | str]:
        """
        TTM Squeeze occurs when Bollinger Bands contract within Keltner Channels.
        EMA ribbon stacked: 13 > 21 > 55 (Uptrend), 13 < 21 < 55 (Downtrend).
        """
        in_squeeze = (bb_upper < keltner_upper) and (bb_lower > keltner_lower)
        is_bull_stacked = (ema13 > ema21) and (ema21 > ema55)
        is_bear_stacked = (ema13 < ema21) and (ema21 < ema55)
        
        bias = "BULLISH" if is_bull_stacked else ("BEARISH" if is_bear_stacked else "NEUTRAL_CHOP")
        
        return {
            "in_squeeze": in_squeeze,
            "ema_trend": bias,
            "squeeze_status": "SQUEEZE_ON" if in_squeeze else "SQUEEZE_FIRED"
        }

    @staticmethod
    def calculate_midpoint_entry(signal_bar_open: float, signal_bar_close: float) -> float:
        """
        50% Retracement Entry level on regular candlestick chart.
        """
        return (signal_bar_open + signal_bar_close) / 2.0

    @staticmethod
    def evaluate_dynamic_legging(
        initial_leg: str,
        initial_credit: float,
        current_underlying_move_pct: float,
        days_to_expiration: int
    ) -> Dict[str, float | str | bool]:
        """
        Legs into wide-wing Iron Condor once underlying establishes direction
        and initial spread reaches profit target.
        """
        should_add_second_leg = False
        second_leg_action = "HOLD"
        
        if initial_leg == "PUT_CREDIT_SPREAD" and current_underlying_move_pct >= 2.0:
            should_add_second_leg = True
            second_leg_action = "SELL_CALL_CREDIT_SPREAD_AT_PEAK"
        elif initial_leg == "CALL_CREDIT_SPREAD" and current_underlying_move_pct <= -2.0:
            should_add_second_leg = True
            second_leg_action = "SELL_PUT_CREDIT_SPREAD_AT_TROUGH"
            
        return {
            "initial_leg": initial_leg,
            "should_add_second_leg": should_add_second_leg,
            "second_leg_action": second_leg_action,
            "resulting_structure": "DYNAMIC_IRON_CONDOR" if should_add_second_leg else "DIRECTIONAL_CREDIT_SPREAD",
            "decay_acceleration": "MAX_THETA_8_DAY_ZONE" if days_to_expiration <= 8 else "NORMAL_DECAY"
        }
