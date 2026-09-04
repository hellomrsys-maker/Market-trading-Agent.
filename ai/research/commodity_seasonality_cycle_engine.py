"""
Agricultural & Energy Seasonality Cycles & Weather Premium Engine (Module AU1 - Python)
Synthesizes Carley Garner's "A Trader's First Book on Commodities":
- Multi-Decade Historical Seasonal Tendency Score (Grains Spring Rally vs Fall Harvest, Energy Summer Driving vs Winter Drawdown)
- Weather Risk Premium & Frost/Drought Volatility Surge Multiplier
- Seasonal Spread Arbitrage Geometry (July vs November Soybeans, March vs December Corn)
"""

from typing import Dict, List, Any


class CommoditySeasonalityCycleEngine:
    # Historical monthly seasonal tendency bias (+1 Strong Bullish to -1 Strong Bearish)
    SEASONAL_PATTERNS = {
        "ZC": {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.6, 5: 0.8, 6: 0.7, 7: -0.2, 8: -0.5, 9: -0.8, 10: -0.7, 11: 0.1, 12: 0.4},
        "ZS": {1: 0.0, 2: 0.2, 3: 0.4, 4: 0.5, 5: 0.7, 6: 0.8, 7: 0.3, 8: -0.4, 9: -0.8, 10: -0.7, 11: 0.2, 12: 0.3},
        "CL": {1: -0.3, 2: 0.2, 3: 0.5, 4: 0.7, 5: 0.8, 6: 0.6, 7: 0.4, 8: 0.2, 9: -0.4, 10: -0.6, 11: -0.5, 12: -0.1},
        "NG": {1: 0.6, 2: 0.3, 3: -0.5, 4: -0.7, 5: -0.3, 6: 0.2, 7: 0.4, 8: 0.1, 9: 0.5, 10: 0.8, 11: 0.9, 12: 0.7}
    }

    def __init__(self):
        pass

    def evaluate_seasonal_bias(
        self,
        symbol: str,
        current_month: int,
        weather_shock_severity: float = 0.0
    ) -> Dict[str, Any]:
        """
        weather_shock_severity: 0.0 (Normal) to 1.0 (Severe Frost / Heat Dome)
        """
        pattern = self.SEASONAL_PATTERNS.get(symbol.upper(), {})
        base_bias = pattern.get(current_month, 0.0)

        # Weather shock elevates positive seasonal bias in grains / natural gas
        adjusted_bias = base_bias + (weather_shock_severity * 0.5)
        clamped_bias = max(-1.0, min(1.0, adjusted_bias))

        regime = "SEASONAL_NEUTRAL"
        if clamped_bias >= 0.5:
            regime = "STRONG_SEASONAL_BULL_WINDOW"
        elif clamped_bias <= -0.5:
            regime = "STRONG_SEASONAL_BEAR_HARVEST_PRESSURE"

        return {
            "symbol": symbol.upper(),
            "month": current_month,
            "base_seasonal_score": round(base_bias, 2),
            "weather_shock_severity": weather_shock_severity,
            "adjusted_seasonal_score": round(clamped_bias, 2),
            "regime": regime,
            "trade_bias": "LONG_FAVORED" if clamped_bias > 0.3 else ("SHORT_FAVORED" if clamped_bias < -0.3 else "NEUTRAL")
        }

    def evaluate_old_crop_new_crop_spread(
        self,
        old_crop_price: float,
        new_crop_price: float,
        historical_spread_mean: float
    ) -> Dict[str, Any]:
        """
        Evaluates July (Old Crop) vs. November (New Crop) Soybeans or March vs. Dec Corn.
        Spread = Old Crop - New Crop (Inversion indicates severe spot supply shortage).
        """
        current_spread = old_crop_price - new_crop_price
        spread_discrepancy = current_spread - historical_spread_mean

        is_inverted = current_spread > 0.0

        return {
            "old_crop_price": old_crop_price,
            "new_crop_price": new_crop_price,
            "current_spread": round(current_spread, 2),
            "historical_mean": round(historical_spread_mean, 2),
            "is_inverted_market": is_inverted,
            "signal": "ENTER_BULL_INVERSION_SPREAD" if spread_discrepancy > 25.0 else "FAIR_VALUE_SPREAD"
        }
