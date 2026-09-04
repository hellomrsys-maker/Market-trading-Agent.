"""
Volume Spread Analysis & False Breakout / Trap Filter Engine (Module BC1 - Python)
Synthesizes "Trade Chart Patterns Guide":
- Breakout Volume Surge Ratio: Vol / SMA20(Vol) >= 1.50
- Wyckoff Spring & Upthrust (Bull/Bear Trap) Detector
- Neckline Pullback / Throwback Retest Confirmation
"""

from typing import Dict, List, Any


class VolumeBreakoutTrapFilter:
    def __init__(self, min_volume_surge_multiplier: float = 1.50):
        self.min_surge = min_volume_surge_multiplier

    def evaluate_breakout_volume(
        self,
        breakout_bar_volume: float,
        sma20_volume: float,
        is_breakout_candle_closed: bool
    ) -> Dict[str, Any]:
        """
        Confirms breakout validity via volume expansion.
        """
        surge_ratio = breakout_bar_volume / max(1.0, sma20_volume)
        is_volume_confirmed = surge_ratio >= self.min_surge and is_breakout_candle_closed

        return {
            "breakout_volume": breakout_bar_volume,
            "sma20_volume": sma20_volume,
            "volume_surge_ratio": round(surge_ratio, 2),
            "is_volume_confirmed": is_volume_confirmed,
            "verdict": "GENUINE_VOLUME_BREAKOUT" if is_volume_confirmed else "LOW_VOLUME_SUSPECT_BREAKOUT"
        }

    def detect_wyckoff_trap(
        self,
        key_level: float,
        extreme_price_during_breakout: float,
        closing_price_after_breakout: float,
        is_support_level: bool = True
    ) -> Dict[str, Any]:
        """
        Spring: Breaches support below key_level but closes back above (Bull Trap for shorts).
        Upthrust: Breaches resistance above key_level but closes back below (Bear Trap for longs).
        """
        if is_support_level:
            # Spring detection
            did_breach = extreme_price_during_breakout < key_level
            did_close_inside = closing_price_after_breakout >= key_level
            is_spring = did_breach and did_close_inside
            trap_name = "WYCKOFF_SPRING_BULL_REVERSAL" if is_spring else "CLEAN_SUPPORT_ACTION"
        else:
            # Upthrust detection
            did_breach = extreme_price_during_breakout > key_level
            did_close_inside = closing_price_after_breakout <= key_level
            is_upthrust = did_breach and did_close_inside
            trap_name = "WYCKOFF_UPTHRUST_BEAR_REVERSAL" if is_upthrust else "CLEAN_RESISTANCE_ACTION"

        is_trap = (is_support_level and is_spring) or (not is_support_level and is_upthrust)

        return {
            "key_level": key_level,
            "extreme_price": extreme_price_during_breakout,
            "closing_price": closing_price_after_breakout,
            "is_trap_detected": is_trap,
            "trap_type": trap_name,
            "trade_action": "FADE_FALSE_BREAKOUT" if is_trap else "FOLLOW_TREND"
        }
