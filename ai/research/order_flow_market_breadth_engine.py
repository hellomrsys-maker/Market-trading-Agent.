"""
Module BK1: Institutional Option Flow, Market Breadth & Persistent Pullback Engine
Synthesized from Bob Lang & Monika Jansen's 'Know Your Options (2nd Edition)'.
"""

from typing import Dict, Any, List
import numpy as np

class OrderFlowMarketBreadthEngine:
    def __init__(self, flow_unusual_mult: float = 5.0):
        self.flow_unusual_mult = flow_unusual_mult

    def audit_option_order_flow(
        self,
        daily_option_volume: float,
        average_30d_volume: float,
        call_volume: float,
        put_volume: float
    ) -> Dict[str, Any]:
        ratio = daily_option_volume / max(1.0, average_30d_volume)
        is_unusual = ratio >= self.flow_unusual_mult
        put_call_ratio = put_volume / max(1.0, call_volume)

        sentiment = "NEUTRAL"
        if is_unusual:
            sentiment = "BULLISH_INSTITUTIONAL_ACCUMULATION" if call_volume > put_volume else "BEARISH_INSTITUTIONAL_DISTRIBUTION"

        return {
            "daily_volume": daily_option_volume,
            "avg_30d_volume": average_30d_volume,
            "flow_ratio": round(ratio, 2),
            "is_unusual_flow": is_unusual,
            "put_call_ratio": round(put_call_ratio, 3),
            "institutional_sentiment": sentiment
        }

    def compute_arms_trin(
        self,
        advancing_issues: float,
        declining_issues: float,
        advancing_volume: float,
        declining_volume: float
    ) -> Dict[str, Any]:
        ad_ratio = advancing_issues / max(1.0, declining_issues)
        vol_ratio = advancing_volume / max(1.0, declining_volume)
        trin = ad_ratio / max(0.001, vol_ratio)

        regime = "NORMAL"
        if trin >= 1.50:
            regime = "EXTREME_FEAR_CONTRARIAN_BULLISH"
        elif trin <= 0.40:
            regime = "EXTREME_GREED_CONTRARIAN_BEARISH"

        return {
            "trin_value": round(trin, 3),
            "regime": regime,
            "is_contrarian_opportunity": trin >= 1.50 or trin <= 0.40
        }

    def evaluate_landry_trend_knockout(
        self,
        closes: List[float],
        highs: List[float],
        lows: List[float],
        persistent_days: int = 15
    ) -> Dict[str, Any]:
        if len(closes) < persistent_days + 3:
            return {"pattern_valid": False, "reason": "INSUFFICIENT_DATA"}

        trend_closes = closes[-persistent_days - 3 : -3]
        x = np.arange(len(trend_closes))
        slope, _ = np.polyfit(x, trend_closes, 1)

        is_persistent_uptrend = slope > 0.10

        tko_bar_high = highs[-2]
        tko_bar_low = lows[-2]
        tko_bar_range = tko_bar_high - tko_bar_low

        prev_low_1 = lows[-3]
        prev_low_2 = lows[-4]
        avg_prior_range = np.mean([highs[i] - lows[i] for i in range(-5, -2)])

        is_wide_range_bar = tko_bar_range >= 1.5 * avg_prior_range
        took_out_prior_lows = (tko_bar_low < prev_low_1) and (tko_bar_low < prev_low_2)

        is_tko = is_persistent_uptrend and is_wide_range_bar and took_out_prior_lows
        current_resumption = closes[-1] > closes[-2]

        return {
            "is_persistent_uptrend": bool(is_persistent_uptrend),
            "trend_slope": round(float(slope), 4),
            "is_wide_range_bar": bool(is_wide_range_bar),
            "took_out_prior_2_lows": bool(took_out_prior_lows),
            "is_tko_pattern": bool(is_tko),
            "trend_resumption_triggered": bool(is_tko and current_resumption),
            "signal": "BUY_PULLBACK_RESUMPTION" if (is_tko and current_resumption) else "MONITORING"
        }