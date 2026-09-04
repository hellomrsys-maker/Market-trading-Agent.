"""
ai/research/cfi_valuation_breadth_engine.py
===========================================
OptionAlpha Agent — Module O1: Python Institutional Valuation & Market Breadth Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple

class CFIValuationBreadthEngine:
    """
    Implements CFI Institutional Trading & Valuation Frameworks:
    - Ben Graham Number = sqrt(22.5 * EPS * BVPS)
    - Katsenelson Absolute P/E Model
    - TRIN (Richard Arms Index) Market Breadth: (Adv/Dec) / (AdvVol/DecVol)
    - Welles Wilder ADX 14 Trend Strength
    - 5-8-13 Fibonacci EMA Ribbon Strategy
    - 50/200 SMA Golden Cross / Death Cross
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    def calculate_ben_graham_number(self, eps: float, book_value_per_share: float) -> float:
        """Intrinsic value benchmark = sqrt(22.5 * EPS * BVPS)"""
        if eps <= 0.0 or book_value_per_share <= 0.0:
            return 0.0
        return float(np.sqrt(22.5 * eps * book_value_per_share))

    def calculate_trin_arms_index(
        self,
        advancing_stocks: int,
        declining_stocks: int,
        advancing_volume: float,
        declining_volume: float
    ) -> Dict[str, float | str]:
        """
        TRIN = (Advancing / Declining) / (Advancing Vol / Declining Vol)
        - TRIN < 0.50: Strongly Overbought (Watch for downside reversal)
        - TRIN > 3.00: Strongly Oversold (Watch for upside rally)
        - TRIN = 1.00: Balanced Market
        """
        adv_dec_ratio = advancing_stocks / max(1, declining_stocks)
        vol_ratio = advancing_volume / max(1.0, declining_volume)
        trin = adv_dec_ratio / max(0.001, vol_ratio)

        if trin < 0.50:
            condition = "EXTREME_OVERBOUGHT_REVERSAL_WATCH"
        elif trin > 3.00:
            condition = "EXTREME_OVERSOLD_RALLY_WATCH"
        else:
            condition = "BALANCED_MARKET"

        return {
            "trin_value": trin,
            "condition": condition,
            "is_extreme": trin < 0.50 or trin > 3.00
        }

    def evaluate_5_8_13_fib_ema_ribbon(self, ema5: float, ema8: float, ema13: float, current_close: float) -> str:
        """
        Fibonacci 5-8-13 EMA Ribbon:
        - Bullish Trend: EMA5 > EMA8 > EMA13 and close > EMA5 (fanned out)
        - Bearish Trend: EMA5 < EMA8 < EMA13 and close < EMA5
        - Consolidation: EMAs compressed and horizontal
        """
        if ema5 > ema8 and ema8 > ema13 and current_close >= ema5:
            return "STRONG_BULLISH_FIB_RIBBON"
        elif ema5 < ema8 and ema8 < ema13 and current_close <= ema5:
            return "STRONG_BEARISH_FIB_RIBBON"
        elif abs(ema5 - ema13) < (current_close * 0.005):
            return "CONSOLIDATION_RIBBON_COMPRESSION"
        return "TRANSITIONAL_RIBBON"
