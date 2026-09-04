"""
agent/risk/portfolio_risk.py
=============================
OptionAlpha Agent — Portfolio Value-at-Risk (VaR) Engine

Computes Parametric and Delta-Normal 99% 1-Day Value-at-Risk (VaR),
Expected Shortfall (CVaR), and Greek sensitivity risk bounds.
"""

from __future__ import annotations

import math
from typing import Dict, List
import numpy as np


class PortfolioRiskEngine:
    """
    Computes portfolio-level multi-asset options VaR and risk bounds.
    """

    @staticmethod
    def calculate_var(
        portfolio_equity: float,
        net_delta_dollars: float,
        net_gamma_dollars: float,
        net_vega_dollars: float,
        daily_underlying_vol: float = 0.015,
        confidence_level: float = 0.99,
        horizon_days: int = 1,
    ) -> Dict:
        """
        Computes 1-day 99% Delta-Gamma VaR and Expected Shortfall.
        """
        # Normal inverse CDF z-score (2.326 for 99%, 1.645 for 95%)
        z = 2.326 if confidence_level >= 0.99 else 1.645

        # 1. First-Order (Delta) Risk
        delta_risk = abs(net_delta_dollars) * daily_underlying_vol * z * math.sqrt(horizon_days)

        # 2. Second-Order (Gamma) Convexity Shock
        gamma_shock_move = daily_underlying_vol * z
        gamma_impact = 0.5 * net_gamma_dollars * (gamma_shock_move ** 2)

        # 3. Vega Shock (assuming 2 vol percentage points shock)
        vega_shock = abs(net_vega_dollars) * 2.0

        # Total 1-day 99% Parametric VaR
        total_var_dollars = max(0.0, delta_risk - gamma_impact + vega_shock)
        var_pct_of_equity = (total_var_dollars / max(1.0, portfolio_equity)) * 100.0

        # Conditional VaR (Expected Shortfall CVaR = ~1.15x VaR under Gaussian assumptions)
        cvar_dollars = total_var_dollars * 1.18

        return {
            "confidence_level": confidence_level,
            "horizon_days": horizon_days,
            "var_99_dollars": round(total_var_dollars, 2),
            "var_99_pct": round(var_pct_of_equity, 3),
            "cvar_dollars": round(cvar_dollars, 2),
            "delta_risk_component": round(delta_risk, 2),
            "gamma_impact_component": round(gamma_impact, 2),
            "vega_risk_component": round(vega_shock, 2),
            "is_var_within_bounds": var_pct_of_equity <= 3.0,  # Max 3% daily portfolio VaR
        }
