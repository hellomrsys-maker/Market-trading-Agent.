"""
Dynamic Covered Call Yield & Dividend Capture Optimizer Engine (Module AP1 - Python)
Synthesizes Will Weiser's "Options Trading For Beginners 2022":
- Covered Call Strike Selection by Market Bias (Growth OTM, Income ATM, Defensive ITM)
- Ex-Dividend Early Assignment Risk Auditor: Extrinsic Value < Dividend per Share
- Total Return Yield Attribution: (Option Premium + Dividends + Cap Appreciation) / Initial Cost Basis
"""

import math
from typing import Dict, List, Any


class CoveredCallYieldEngine:
    def __init__(self):
        pass

    def evaluate_covered_call(
        self,
        stock_cost_basis: float,
        current_spot: float,
        strike_price: float,
        call_premium: float,
        dte_days: float,
        impending_dividend_per_share: float = 0.0
    ) -> Dict[str, Any]:
        """
        Evaluates yield, capital appreciation potential, and downside protection.
        """
        # Downside cushion
        breakeven_price = stock_cost_basis - call_premium
        downside_protection_pct = (call_premium / current_spot) * 100.0

        # Static yield (if stock unchanged at expiration)
        static_profit = call_premium + impending_dividend_per_share
        static_yield_pct = (static_profit / stock_cost_basis) * 100.0
        annualized_static_yield = static_yield_pct * (365.0 / max(1.0, dte_days))

        # Max yield (if stock called away at strike)
        cap_gain = max(0.0, strike_price - stock_cost_basis)
        max_profit_total = cap_gain + call_premium + impending_dividend_per_share
        max_yield_pct = (max_profit_total / stock_cost_basis) * 100.0
        annualized_max_yield = max_yield_pct * (365.0 / max(1.0, dte_days))

        # Early assignment risk check (if ITM and dividend approaching)
        intrinsic_val = max(0.0, current_spot - strike_price)
        extrinsic_val = max(0.0, call_premium - intrinsic_val)
        
        is_early_assignment_risk = (current_spot > strike_price) and (extrinsic_val < impending_dividend_per_share)

        return {
            "stock_cost_basis": stock_cost_basis,
            "current_spot": current_spot,
            "strike_price": strike_price,
            "call_premium": call_premium,
            "breakeven_price": round(breakeven_price, 2),
            "downside_protection_pct": round(downside_protection_pct, 2),
            "static_yield_pct": round(static_yield_pct, 2),
            "annualized_static_yield_pct": round(annualized_static_yield, 2),
            "max_yield_pct": round(max_yield_pct, 2),
            "annualized_max_yield_pct": round(annualized_max_yield, 2),
            "extrinsic_value": round(extrinsic_val, 3),
            "dividend_per_share": impending_dividend_per_share,
            "early_assignment_warning": is_early_assignment_risk
        }
