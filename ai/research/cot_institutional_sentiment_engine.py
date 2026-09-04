"""
COT (Commitment of Traders) Institutional Positioning & Sentiment Engine (Module AM1 - Python)
Synthesizes Jack D. Schwager's "A Complete Guide to the Futures Market":
- 3-Year Rolling COT Percentile Index: (Current - Min) / (Max - Min) * 100
- Commercial Hedger vs Non-Commercial Speculator Extreme Divergence
- Open Interest Trend Confirmation Matrix (Price + Open Interest)
"""

from typing import Dict, List, Any


class CotInstitutionalSentimentEngine:
    def __init__(self, extreme_bullish_threshold: float = 90.0, extreme_bearish_threshold: float = 10.0):
        self.extreme_bull = extreme_bullish_threshold
        self.extreme_bear = extreme_bearish_threshold

    def calculate_cot_index(
        self,
        current_net_position: float,
        min_net_3yr: float,
        max_net_3yr: float
    ) -> Dict[str, Any]:
        """
        COT Index = (Current - Min) / (Max - Min) * 100%
        """
        rng = max(1.0, max_net_3yr - min_net_3yr)
        index = ((current_net_position - min_net_3yr) / rng) * 100.0
        clamped_index = max(0.0, min(100.0, index))

        is_extreme_bull = clamped_index >= self.extreme_bull
        is_extreme_bear = clamped_index <= self.extreme_bear

        status = "NEUTRAL"
        if is_extreme_bull:
            status = "EXTREME_COMMERCIAL_ACCUMULATION_BULLISH"
        elif is_extreme_bear:
            status = "EXTREME_COMMERCIAL_DISTRIBUTION_BEARISH"

        return {
            "current_net": current_net_position,
            "cot_index_pct": round(clamped_index, 2),
            "status": status,
            "is_extreme_signal": is_extreme_bull or is_extreme_bear
        }

    def evaluate_price_oi_confluence(
        self,
        price_change: float,
        oi_change: float
    ) -> Dict[str, Any]:
        """
        Schwager Open Interest Interpretation Matrix:
        Price Up + OI Up   => Aggressive New Long Accumulation (Strong Bullish)
        Price Up + OI Down => Short Covering Rally (Vulnerable Bullish)
        Price Dn + OI Up   => Aggressive New Short Selling (Strong Bearish)
        Price Dn + OI Down => Long Liquidation (Vulnerable Bearish)
        """
        if price_change > 0 and oi_change > 0:
            regime = "STRONG_BULLISH_NEW_LONGS"
            bias = "BUY_MOMENTUM"
        elif price_change > 0 and oi_change <= 0:
            regime = "WEAK_BULLISH_SHORT_COVERING"
            bias = "FADE_OR_TIGHTEN_STOPS"
        elif price_change < 0 and oi_change > 0:
            regime = "STRONG_BEARISH_NEW_SHORTS"
            bias = "SELL_MOMENTUM"
        elif price_change < 0 and oi_change <= 0:
            regime = "WEAK_BEARISH_LONG_LIQUIDATION"
            bias = "PREPARE_FOR_REVERSAL_BOUNCE"
        else:
            regime = "NEUTRAL_CONSOLIDATION"
            bias = "WAIT"

        return {
            "price_change": price_change,
            "oi_change": oi_change,
            "regime": regime,
            "bias": bias
        }
