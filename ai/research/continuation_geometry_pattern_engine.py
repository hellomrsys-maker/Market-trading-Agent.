"""
Bilateral & Continuation Geometric Pattern Engine (Module BB1 - Python)
Synthesizes "Trade Chart Patterns Guide":
- Triangle Formations (Ascending, Descending, Symmetrical) with Apex Compression
- Bull & Bear Flags and Pennants with Measured Flagpole Targets
- Rising & Falling Wedges
"""

from typing import Dict, List, Any


class ContinuationGeometryPatternEngine:
    def __init__(self):
        pass

    def evaluate_triangle_pattern(
        self,
        upper_trendline_slope: float,
        lower_trendline_slope: float,
        pattern_base_height: float,
        breakout_price: float,
        current_spot: float
    ) -> Dict[str, Any]:
        """
        Ascending: upper ~ 0, lower > 0 (Bullish)
        Descending: lower ~ 0, upper < 0 (Bearish)
        Symmetrical: upper < 0, lower > 0 (Bilateral)
        """
        if abs(upper_trendline_slope) < 0.05 and lower_trendline_slope > 0.05:
            pattern_type = "ASCENDING_TRIANGLE_BULLISH"
            target = breakout_price + pattern_base_height
            is_breakout = current_spot > breakout_price
        elif abs(lower_trendline_slope) < 0.05 and upper_trendline_slope < -0.05:
            pattern_type = "DESCENDING_TRIANGLE_BEARISH"
            target = breakout_price - pattern_base_height
            is_breakout = current_spot < breakout_price
        else:
            pattern_type = "SYMMETRICAL_TRIANGLE_BILATERAL"
            target = (breakout_price + pattern_base_height) if current_spot > breakout_price else (breakout_price - pattern_base_height)
            is_breakout = abs(current_spot - breakout_price) > 0.5

        return {
            "pattern_type": pattern_type,
            "base_height": round(pattern_base_height, 2),
            "breakout_price": breakout_price,
            "measured_target": round(target, 2),
            "is_breakout_confirmed": is_breakout
        }

    def evaluate_flag_or_pennant(
        self,
        flagpole_start_price: float,
        flagpole_peak_price: float,
        breakout_price: float,
        current_spot: float,
        is_bull_flag: bool = True
    ) -> Dict[str, Any]:
        """
        Flagpole Height = Peak - Start. Target = Breakout + Flagpole.
        """
        flagpole_height = abs(flagpole_peak_price - flagpole_start_price)
        if is_bull_flag:
            target = breakout_price + flagpole_height
            is_breakout = current_spot > breakout_price
            name = "BULL_FLAG_CONTINUATION"
        else:
            target = breakout_price - flagpole_height
            is_breakout = current_spot < breakout_price
            name = "BEAR_FLAG_CONTINUATION"

        return {
            "pattern_name": name,
            "flagpole_height": round(flagpole_height, 2),
            "breakout_price": breakout_price,
            "measured_target": round(target, 2),
            "is_breakout_confirmed": is_breakout
        }
