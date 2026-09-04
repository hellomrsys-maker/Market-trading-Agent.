"""
Volatility Skew, Smile Geometry & Ratio Arbitrage Engine (Module AY1 - Python)
Synthesizes Mark Sebastian's "Trading Options for Edge":
- Horizontal Term Structure vs. Vertical Strike Skew Geometry
- Skew Ratio Arbitrage & Broken Wing Butterfly (BWB) Zero-Downside Risk Optimizer
- Extreme Put Skew vs. Flat Call Skew Strategy Selector
"""

from typing import Dict, List, Any


class VolatilitySkewArbitrageEngine:
    def __init__(self, steep_skew_threshold: float = 0.25):
        self.steep_skew_threshold = steep_skew_threshold

    def analyze_skew_geometry(
        self,
        iv_atm: float,
        iv_25d_put: float,
        iv_25d_call: float,
        iv_30d_term: float,
        iv_90d_term: float
    ) -> Dict[str, Any]:
        """
        Computes Strike Skew Slope and Term Structure Slope.
        Strike Skew Slope = (IV_25d_Put - IV_25d_Call) / IV_ATM
        Term Structure Slope = (IV_90d - IV_30d) / IV_30d
        """
        strike_skew_slope = (iv_25d_put - iv_25d_call) / max(1e-4, iv_atm)
        term_slope = (iv_90d_term - iv_30d_term) / max(1e-4, iv_30d_term)

        is_steep_put_skew = strike_skew_slope >= self.steep_skew_threshold
        is_contango_term = term_slope > 0.05

        optimal_structure = "STANDARD_VERTICAL_OR_CONDOR"
        if is_steep_put_skew:
            optimal_structure = "PUT_BROKEN_WING_BUTTERFLY_OR_1X2_RATIO_SPREAD"
        elif strike_skew_slope < 0.05:
            optimal_structure = "CALL_BACKSPREAD_OR_REVERSE_CALENDAR"

        return {
            "iv_atm": iv_atm,
            "strike_skew_slope": round(strike_skew_slope, 4),
            "term_structure_slope": round(term_slope, 4),
            "is_steep_put_skew": is_steep_put_skew,
            "is_contango_term": is_contango_term,
            "optimal_structure": optimal_structure
        }

    def structure_broken_wing_butterfly(
        self,
        spot_price: float,
        lower_long_strike: float,
        middle_short_strike: float,
        upper_long_strike: float,
        cost_lower_long: float,
        premium_short_middle: float,
        cost_upper_long: float
    ) -> Dict[str, Any]:
        """
        Structures 1:2:1 Broken Wing Butterfly (BWB).
        Net Credit = 2 * premium_short_middle - cost_lower_long - cost_upper_long
        Zero risk in one direction if Net Credit >= 0.
        """
        net_credit = (2.0 * premium_short_middle) - cost_lower_long - cost_upper_long
        has_zero_downside_risk = net_credit >= 0.0

        max_profit_strike = middle_short_strike
        max_profit = (middle_short_strike - lower_long_strike) + net_credit

        return {
            "spot_price": spot_price,
            "lower_strike": lower_long_strike,
            "middle_strike": middle_short_strike,
            "upper_strike": upper_long_strike,
            "net_credit_received": round(net_credit, 2),
            "max_profit_potential": round(max_profit, 2),
            "has_zero_downside_risk": has_zero_downside_risk,
            "skew_edge_status": "HIGH_PROBABILITY_ASYMMETRIC_EDGE" if has_zero_downside_risk else "STANDARD_DEBIT_BWB"
        }
