"""
Trading Firm Greek Inventory Governance & Vega/Gamma Risk Budgeting Engine (Module AX1 - Python)
Synthesizes Mark Sebastian's "Trading Options for Edge":
- Professional Greek Inventory Limits (Net Delta, Gamma Rent Ratio = Theta / (0.5 * Gamma * S^2 * sigma^2))
- Sector Vega Exposure Capping (< 8.0% Portfolio Equity)
- 3D Greek Stress Testing Matrix (Price +-10%, IV +-25%, Time +7d)
"""

import math
from typing import Dict, List, Any


class TradingFirmGreekGovernor:
    def __init__(
        self,
        max_delta_limit: float = 50.0,
        min_gamma_rent_ratio: float = 1.0,
        max_vega_pct_equity: float = 8.0
    ):
        self.max_delta = max_delta_limit
        self.min_rent_ratio = min_gamma_rent_ratio
        self.max_vega_pct = max_vega_pct_equity

    def evaluate_greek_inventory(
        self,
        portfolio_delta: float,
        portfolio_gamma: float,
        portfolio_theta: float,
        portfolio_vega: float,
        spot_price: float,
        iv_annual: float,
        account_equity: float
    ) -> Dict[str, Any]:
        """
        Audits Greek inventory against market maker trading firm rules.
        """
        # Gamma Rent calculation
        daily_sigma = iv_annual / math.sqrt(252.0)
        daily_gamma_cost = 0.5 * abs(portfolio_gamma) * (spot_price ** 2) * (daily_sigma ** 2)
        rent_ratio = abs(portfolio_theta) / max(1e-4, daily_gamma_cost)

        # Vega risk as % of equity
        vega_exposure_dollars = abs(portfolio_vega) * 100.0  # $ per 1% vol move
        vega_pct_equity = (vega_exposure_dollars / max(1.0, account_equity)) * 100.0

        is_delta_ok = abs(portfolio_delta) <= self.max_delta
        is_rent_ok = rent_ratio >= self.min_rent_ratio
        is_vega_ok = vega_pct_equity <= self.max_vega_pct

        is_compliant = is_delta_ok and is_rent_ok and is_vega_ok

        return {
            "portfolio_delta": round(portfolio_delta, 2),
            "portfolio_gamma": round(portfolio_gamma, 4),
            "portfolio_theta": round(portfolio_theta, 2),
            "portfolio_vega": round(portfolio_vega, 2),
            "gamma_rent_ratio": round(rent_ratio, 2),
            "vega_pct_equity": round(vega_pct_equity, 2),
            "is_delta_compliant": is_delta_ok,
            "is_rent_compliant": is_rent_ok,
            "is_vega_compliant": is_vega_ok,
            "is_firm_approved": is_compliant,
            "governance_action": "GREEKS_BALANCED_APPROVED" if is_compliant else "REBALANCE_OR_REDUCE_GREEK_INVENTORY"
        }

    def stress_test_greek_matrix(
        self,
        portfolio_delta: float,
        portfolio_gamma: float,
        portfolio_theta: float,
        portfolio_vega: float,
        spot_price: float
    ) -> Dict[str, float]:
        """
        Computes Taylor series PnL impact across standard trading firm scenarios.
        """
        scenarios = {
            "crash_down_10pct_vol_up_25pct": (-0.10 * spot_price) * portfolio_delta + 0.5 * portfolio_gamma * ((-0.10 * spot_price) ** 2) + 25.0 * portfolio_vega - 1.0 * portfolio_theta,
            "rally_up_10pct_vol_down_10pct": (0.10 * spot_price) * portfolio_delta + 0.5 * portfolio_gamma * ((0.10 * spot_price) ** 2) - 10.0 * portfolio_vega - 1.0 * portfolio_theta,
            "unchanged_price_time_decay_7d": 7.0 * portfolio_theta
        }
        return {k: round(v, 2) for k, v in scenarios.items()}
