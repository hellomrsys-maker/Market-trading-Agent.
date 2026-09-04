"""
Classical Reversal Pattern Recognition Engine (Module BA1 - Python)
Synthesizes "Trade Chart Patterns Guide":
- Head & Shoulders (Standard & Inverse) Detection with Necklines and Measured Move Targets
- Double Tops (M-Pattern) & Double Bottoms (W-Pattern) with 1.5% Peak/Trough Tolerance
- Rounding Bottoms (Saucers) and V-Reversals
"""

import math
from typing import Dict, List, Any


class ClassicalReversalPatternEngine:
    def __init__(self, tolerance_pct: float = 1.5):
        self.tolerance_pct = tolerance_pct

    def evaluate_head_and_shoulders(
        self,
        left_shoulder_peak: float,
        head_peak: float,
        right_shoulder_peak: float,
        neckline_price: float,
        current_spot: float,
        is_inverse: bool = False
    ) -> Dict[str, Any]:
        """
        Head & Shoulders (Standard Bearish Reversal) or Inverse H&S (Bullish Reversal).
        Target = Neckline Breakout Price +- (Head Peak - Neckline Price)
        """
        if not is_inverse:
            # Standard H&S: Head must be higher than both shoulders
            is_valid_structure = (head_peak > left_shoulder_peak) and (head_peak > right_shoulder_peak)
            shoulder_symmetry = abs(left_shoulder_peak - right_shoulder_peak) / max(1.0, head_peak) <= (self.tolerance_pct / 100.0 * 2.0)
            
            pattern_height = head_peak - neckline_price
            measured_target = neckline_price - pattern_height
            is_breakout_confirmed = current_spot < neckline_price
            pattern_name = "HEAD_AND_SHOULDERS_BEARISH"
        else:
            # Inverse H&S: Head (trough) must be lower than both shoulders
            is_valid_structure = (head_peak < left_shoulder_peak) and (head_peak < right_shoulder_peak)
            shoulder_symmetry = abs(left_shoulder_peak - right_shoulder_peak) / max(1.0, left_shoulder_peak) <= (self.tolerance_pct / 100.0 * 2.0)
            
            pattern_height = neckline_price - head_peak
            measured_target = neckline_price + pattern_height
            is_breakout_confirmed = current_spot > neckline_price
            pattern_name = "INVERSE_HEAD_AND_SHOULDERS_BULLISH"

        is_active = is_valid_structure and shoulder_symmetry

        return {
            "pattern_name": pattern_name,
            "is_valid_structure": is_valid_structure,
            "shoulder_symmetry": shoulder_symmetry,
            "neckline_price": neckline_price,
            "pattern_height": round(pattern_height, 2),
            "measured_target": round(measured_target, 2),
            "is_breakout_confirmed": is_breakout_confirmed,
            "status": "CONFIRMED_BREAKOUT_ACTIVE" if (is_active and is_breakout_confirmed) else ("FORMING_SETUP" if is_active else "INVALID_STRUCTURE")
        }

    def evaluate_double_top_bottom(
        self,
        peak1: float,
        peak2: float,
        trough_neckline: float,
        current_spot: float,
        is_double_bottom: bool = False
    ) -> Dict[str, Any]:
        """
        Double Top (M-Pattern) or Double Bottom (W-Pattern).
        """
        peak_diff_pct = (abs(peak1 - peak2) / max(1.0, peak1)) * 100.0
        is_level_aligned = peak_diff_pct <= self.tolerance_pct

        if not is_double_bottom:
            pattern_height = ((peak1 + peak2) / 2.0) - trough_neckline
            measured_target = trough_neckline - pattern_height
            is_breakout = current_spot < trough_neckline
            name = "DOUBLE_TOP_BEARISH"
        else:
            pattern_height = trough_neckline - ((peak1 + peak2) / 2.0)
            measured_target = trough_neckline + pattern_height
            is_breakout = current_spot > trough_neckline
            name = "DOUBLE_BOTTOM_BULLISH"

        return {
            "pattern_name": name,
            "is_level_aligned": is_level_aligned,
            "peak_diff_pct": round(peak_diff_pct, 2),
            "neckline_price": trough_neckline,
            "pattern_height": round(pattern_height, 2),
            "measured_target": round(measured_target, 2),
            "is_breakout_confirmed": is_breakout,
            "status": "BREAKOUT_ACTIVE" if (is_level_aligned and is_breakout) else "MONITORING"
        }
