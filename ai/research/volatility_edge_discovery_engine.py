"""
Volatility Edge Discovery & Realized vs. Implied Mispricing Engine (Module AW1 - Python)
Synthesizes Mark Sebastian's "Trading Options for Edge":
- Realized Volatility (HV) vs. Implied Volatility (IV) Mispricing Spread: Vol Spread = IV - HV
- Overpriced (Short Vol Edge) vs Underpriced (Long Vol Edge) Regimes
- Rolling 52-Week Volatility Cone & IV Percentile Rank
"""

import math
from typing import Dict, List, Any


class VolatilityEdgeDiscoveryEngine:
    def __init__(self, expensive_vol_spread: float = 4.0, cheap_vol_spread: float = -2.0):
        self.expensive_vol = expensive_vol_spread
        self.cheap_vol = cheap_vol_spread

    def calculate_historical_volatility(self, close_prices: List[float], trading_days: int = 252) -> float:
        """
        Standard close-to-close annualized realized volatility.
        """
        n = len(close_prices)
        if n < 2:
            return 0.0

        returns = [math.log(close_prices[i] / close_prices[i - 1]) for i in range(1, n)]
        mean_ret = sum(returns) / len(returns)
        var = sum((r - mean_ret) ** 2 for r in returns) / (len(returns) - 1)
        annualized_hv = math.sqrt(var * trading_days) * 100.0
        return round(annualized_hv, 2)

    def evaluate_volatility_edge(
        self,
        iv_30d: float,
        hv_30d: float,
        iv_52wk_min: float,
        iv_52wk_max: float
    ) -> Dict[str, Any]:
        """
        Computes Volatility Spread = IV - HV and IV Percentile Rank within the 52-week cone.
        """
        vol_spread = iv_30d - hv_30d
        
        # IV Rank
        iv_range = max(1.0, iv_52wk_max - iv_52wk_min)
        iv_rank = ((iv_30d - iv_52wk_min) / iv_range) * 100.0
        clamped_iv_rank = max(0.0, min(100.0, iv_rank))

        is_expensive = (vol_spread >= self.expensive_vol) or (clamped_iv_rank >= 75.0)
        is_cheap = (vol_spread <= self.cheap_vol) or (clamped_iv_rank <= 25.0)

        edge_regime = "FAIR_VALUE_NEUTRAL"
        strategy_recommendation = "CALENDAR_OR_DIRECTIONAL_SPREADS"

        if is_expensive:
            edge_regime = "VOLATILITY_EXPENSIVE_SHORT_VOL_EDGE"
            strategy_recommendation = "SELL_IRON_CONDORS_CREDIT_SPREADS_OR_BUTTERFLIES"
        elif is_cheap:
            edge_regime = "VOLATILITY_CHEAP_LONG_VOL_EDGE"
            strategy_recommendation = "BUY_LONG_STRADDLES_CALENDARS_OR_DEBIT_SPREADS"

        return {
            "iv_30d": iv_30d,
            "hv_30d": hv_30d,
            "vol_spread": round(vol_spread, 2),
            "iv_rank_pct": round(clamped_iv_rank, 1),
            "edge_regime": edge_regime,
            "is_expensive_edge": is_expensive,
            "is_cheap_edge": is_cheap,
            "strategy_recommendation": strategy_recommendation
        }
