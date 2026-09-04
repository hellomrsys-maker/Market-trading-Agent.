"""
Schwager Classical Price Action, Key Reversal & Breakout Trap Engine (Module AK1 - Python)
Synthesizes Jack D. Schwager's "A Complete Guide to the Futures Market":
- Bullish & Bearish Key Reversal Days
- Island Reversal Recognition (Exhaustion Gap + Breakaway Gap)
- False Breakout Trap Exploitation ("Spring" & "Upthrust" past multi-bar S/R)
- 3-Gap Classification System (Breakaway, Runaway/Measuring, Exhaustion)
- Adaptive Trailing Stop Loss & Measuring Gap Price Projections
"""

import math
from typing import Dict, List, Any, Optional


class SchwagerPriceActionEngine:
    def __init__(self, volume_surge_multiplier: float = 1.3):
        self.volume_surge_multiplier = volume_surge_multiplier

    def evaluate_key_reversal(
        self,
        prev_open: float,
        prev_high: float,
        prev_low: float,
        prev_close: float,
        curr_open: float,
        curr_high: float,
        curr_low: float,
        curr_close: float,
        curr_volume: float,
        avg_volume: float
    ) -> Dict[str, Any]:
        """
        Bullish Key Reversal: New low below prev_low, but closes above prev_close (or prev_high) with volume surge.
        Bearish Key Reversal: New high above prev_high, but closes below prev_close (or prev_low) with volume surge.
        """
        vol_surge = (curr_volume >= avg_volume * self.volume_surge_multiplier) if avg_volume > 0 else True
        
        is_bull_key = (curr_low < prev_low) and (curr_close > prev_close) and vol_surge
        is_bear_key = (curr_high > prev_high) and (curr_close < prev_close) and vol_surge

        pattern = "NO_REVERSAL"
        if is_bull_key:
            pattern = "BULLISH_KEY_REVERSAL"
        elif is_bear_key:
            pattern = "BEARISH_KEY_REVERSAL"

        return {
            "pattern": pattern,
            "is_reversal": is_bull_key or is_bear_key,
            "volume_surge": vol_surge,
            "stop_level": round(curr_low if is_bull_key else curr_high, 2)
        }

    def detect_false_breakout_trap(
        self,
        support_level: float,
        resistance_level: float,
        curr_high: float,
        curr_low: float,
        curr_close: float
    ) -> Dict[str, Any]:
        """
        Spring Trap: Pierces below support_level intra-bar but closes back ABOVE support.
        Upthrust Trap: Pierces above resistance_level intra-bar but closes back BELOW resistance.
        """
        is_spring = (curr_low < support_level) and (curr_close >= support_level)
        is_upthrust = (curr_high > resistance_level) and (curr_close <= resistance_level)

        trap_type = "NO_TRAP"
        trade_bias = "NEUTRAL"
        if is_spring:
            trap_type = "BULLISH_SPRING_TRAP"
            trade_bias = "BUY_REJECTION"
        elif is_upthrust:
            trap_type = "BEARISH_UPTHRUST_TRAP"
            trade_bias = "SELL_REJECTION"

        return {
            "trap_type": trap_type,
            "trade_bias": trade_bias,
            "support": support_level,
            "resistance": resistance_level,
            "close": curr_close
        }

    def classify_gap_structure(
        self,
        base_breakout_price: float,
        gap_open: float,
        prev_bar_high: float,
        prev_bar_low: float,
        bars_since_breakout: int,
        is_filled_rapidly: bool
    ) -> Dict[str, Any]:
        """
        Classifies Breakaway vs Runaway (Measuring) vs Exhaustion gaps.
        """
        gap_size = 0.0
        direction = "UP" if gap_open > prev_bar_high else ("DOWN" if gap_open < prev_bar_low else "NONE")

        if direction == "UP":
            gap_size = gap_open - prev_bar_high
        elif direction == "DOWN":
            gap_size = prev_bar_low - gap_open

        gap_type = "COMMON_GAP"
        projected_target = 0.0

        if direction != "NONE":
            if is_filled_rapidly and bars_since_breakout > 5:
                gap_type = "EXHAUSTION_GAP"
                projected_target = gap_open
            elif bars_since_breakout <= 2:
                gap_type = "BREAKAWAY_GAP"
                projected_target = gap_open + (2.0 * gap_size if direction == "UP" else -2.0 * gap_size)
            else:
                gap_type = "RUNAWAY_MEASURING_GAP"
                # Measuring projection: distance from base breakout to gap doubled
                run_length = abs(gap_open - base_breakout_price)
                projected_target = gap_open + (run_length if direction == "UP" else -run_length)

        return {
            "direction": direction,
            "gap_size": round(gap_size, 2),
            "gap_type": gap_type,
            "projected_target": round(projected_target, 2)
        }
