"""
ai/research/order_flow_footprint_engine.py
=========================================
OptionAlpha Agent — Module I1: Python Order Flow Footprint & VPOC Delta Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple

class OrderFlowFootprintEngine:
    """
    Analyzes real-time footprint charts, market order Ask/Bid delta,
    cumulative delta trends, delta divergence, Volume Point of Control (VPOC),
    and Value Area (70% range - VAH/VAL) from Level 2/3 depth.
    """
    def __init__(self):
        # 64-byte synchronized state vector alignment
        self.memory_state = np.zeros(64, dtype=np.float32)
        self.cumulative_delta = 0.0
        self.cumulative_volume = 0.0

    def process_footprint_bar(
        self,
        bid_quantities: List[float],
        ask_quantities: List[float],
        price_levels: List[float]
    ) -> Dict[str, float | str | bool]:
        """
        Calculates bar delta, updates running cumulative delta, and evaluates
        cumulative delta/volume percentage.
        """
        bar_bid_vol = sum(bid_quantities)
        bar_ask_vol = sum(ask_quantities)
        bar_volume = bar_bid_vol + bar_ask_vol
        bar_delta = bar_ask_vol - bar_bid_vol
        
        self.cumulative_delta += bar_delta
        self.cumulative_volume += bar_volume
        
        cum_delta_pct = (self.cumulative_delta / max(1.0, self.cumulative_volume)) * 100.0
        
        # Calculate Volume Profile & VPOC (widest horizontal volume row)
        level_volumes = [b + a for b, a in zip(bid_quantities, ask_quantities)]
        max_idx = int(np.argmax(level_volumes)) if level_volumes else 0
        vpoc = price_levels[max_idx] if price_levels else 0.0
        
        # Calculate Value Area (70% of total bar volume around VPOC)
        total_vol = max(1.0, sum(level_volumes))
        target_vol = 0.70 * total_vol
        sorted_indices = np.argsort(level_volumes)[::-1]
        accumulated_vol = 0.0
        va_prices = []
        for idx in sorted_indices:
            accumulated_vol += level_volumes[idx]
            va_prices.append(price_levels[idx])
            if accumulated_vol >= target_vol:
                break
        
        vah = max(va_prices) if va_prices else vpoc
        val = min(va_prices) if va_prices else vpoc
        
        return {
            "bar_delta": bar_delta,
            "cumulative_delta": self.cumulative_delta,
            "cumulative_volume": self.cumulative_volume,
            "cumulative_delta_volume_pct": cum_delta_pct,
            "vpoc": vpoc,
            "vah": vah,
            "val": val,
            "dominant_side": "AGGRESSIVE_BUYERS" if bar_delta > 0 else "AGGRESSIVE_SELLERS"
        }

    def detect_delta_divergence(
        self,
        price_direction: str,
        delta_direction: str,
        cumulative_delta_trend: str
    ) -> Dict[str, str | bool]:
        """
        Detects exhaustion and reversal conditions based on Delta Divergence:
        - Price rising + Delta falling -> Long Liquidation / Exhaustion (Bearish Reversal Setup)
        - Price falling + Delta rising -> Short Covering / Absorption (Bullish Reversal Setup)
        """
        if price_direction == "RISING" and (delta_direction == "FALLING" or cumulative_delta_trend == "DECREASING"):
            return {
                "divergence_type": "BEARISH_DELTA_DIVERGENCE",
                "warning": "UPTREND_EXHAUSTION_PROFIT_BOOKING",
                "is_reversal_imminent": True
            }
        elif price_direction == "FALLING" and (delta_direction == "RISING" or cumulative_delta_trend == "INCREASING"):
            return {
                "divergence_type": "BULLISH_DELTA_DIVERGENCE",
                "warning": "DOWNTREND_EXHAUSTION_SHORT_COVERING",
                "is_reversal_imminent": True
            }
        return {
            "divergence_type": "CONFIRMED_TREND_FLOW",
            "warning": "HEALTHY_ORDER_FLOW",
            "is_reversal_imminent": False
        }
