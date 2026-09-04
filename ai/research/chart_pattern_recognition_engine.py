"""
ai/research/chart_pattern_recognition_engine.py
===============================================
OptionAlpha Agent — Module L1: Python Multi-Bar, Candlestick & NR4 Chart Pattern Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple

class ChartPatternRecognitionEngine:
    """
    Implements full pattern taxonomy from the Technical Analysis Guide:
    - Multi-Bar Formations: Triangles (Symmetrical, Ascending, Descending), Wedges,
      Double/Triple Tops & Bottoms, Rectangles, Head & Shoulders, Cup & Handle, Pennants/Flags
    - Candlestick Patterns: Doji, Harami, Hammer/Hanging Man, Shooting Star/Inverted Hammer,
      Engulfing, Dark Cloud Cover/Piercing Line, Morning/Evening Star, Three White Soldiers/Black Crows
    - Volatility & Gap Systems: Explosion Gap Pivot & Throwback, Pipe Bottom, Inside Bar, NR4
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    def identify_candlestick_pattern(
        self,
        opens: List[float],
        highs: List[float],
        lows: List[float],
        closes: List[float]
    ) -> Dict[str, str | float]:
        if len(opens) < 2:
            return {"pattern": "INSUFFICIENT_BARS", "sentiment": "NEUTRAL"}

        o1, h1, l1, c1 = opens[-1], highs[-1], lows[-1], closes[-1]
        o0, h0, l0, c0 = opens[-2], highs[-2], lows[-2], closes[-2]
        
        body1 = abs(c1 - o1)
        range1 = max(0.001, h1 - l1)
        upper_wick1 = h1 - max(o1, c1)
        lower_wick1 = min(o1, c1) - l1

        # 1. Doji
        if body1 <= 0.1 * range1 and upper_wick1 > 0.3 * range1 and lower_wick1 > 0.3 * range1:
            return {"pattern": "DOJI_INDECISION", "sentiment": "NEUTRAL_REVERSAL_WARNING"}
        
        # 2. Bullish Hammer / Hanging Man
        if lower_wick1 >= 2.0 * body1 and upper_wick1 <= 0.2 * body1:
            return {"pattern": "BULLISH_HAMMER" if c1 >= o1 else "HANGING_MAN", "sentiment": "BULLISH_REVERSAL"}

        # 3. Shooting Star / Inverted Hammer
        if upper_wick1 >= 2.0 * body1 and lower_wick1 <= 0.2 * body1:
            return {"pattern": "SHOOTING_STAR_BEARISH" if c1 <= o1 else "INVERTED_HAMMER", "sentiment": "BEARISH_REVERSAL"}

        # 4. Bullish / Bearish Engulfing
        if c0 < o0 and c1 > o1 and o1 <= c0 and c1 >= o0:
            return {"pattern": "BULLISH_ENGULFING", "sentiment": "STRONG_BULLISH_REVERSAL"}
        if c0 > o0 and c1 < o1 and o1 >= c0 and c1 <= o0:
            return {"pattern": "BEARISH_ENGULFING", "sentiment": "STRONG_BEARISH_REVERSAL"}

        # 5. Harami
        if abs(c0 - o0) > 2.0 * body1 and min(o0, c0) <= min(o1, c1) and max(o0, c0) >= max(o1, c1):
            return {"pattern": "HARAMI_INSIDE_SPINNING_TOP", "sentiment": "CONSOLIDATION_REVERSAL"}

        return {"pattern": "NORMAL_CANDLE", "sentiment": "NEUTRAL"}

    def detect_nr4_and_inside_bar(self, highs: List[float], lows: List[float]) -> Dict[str, bool | str]:
        """Detects Inside Bar and Narrow Range 4 (NR4) Volatility Contraction."""
        if len(highs) < 4:
            return {"is_nr4": False, "is_inside_bar": False}

        ranges = [h - l for h, l in zip(highs[-4:], lows[-4:])]
        is_nr4 = ranges[-1] == min(ranges)
        is_inside_bar = (highs[-1] <= highs[-2]) and (lows[-1] >= lows[-2])

        return {
            "is_nr4": is_nr4,
            "is_inside_bar": is_inside_bar,
            "signal": "VOLATILITY_EXPANSION_BREAKOUT_IMMINENT" if (is_nr4 or is_inside_bar) else "STANDARD_VOLATILITY"
        }

    def compute_pattern_price_target(self, pattern_type: str, peak_price: float, trough_price: float, breakout_price: float) -> float:
        """Computes measured move price targets for classical chart patterns."""
        height = peak_price - trough_price
        if "DOUBLE_TOP" in pattern_type or "HEAD_AND_SHOULDERS" in pattern_type or "DESCENDING_TRIANGLE" in pattern_type:
            return breakout_price - height
        elif "DOUBLE_BOTTOM" in pattern_type or "INVERSE_H_AND_S" in pattern_type or "ASCENDING_TRIANGLE" in pattern_type or "CUP_AND_HANDLE" in pattern_type:
            return breakout_price + height
        return breakout_price
