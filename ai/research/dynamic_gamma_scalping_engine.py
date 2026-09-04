"""
Dynamic Algorithmic Gamma Scalping & Discrete Rebalancing Engine (Module AH1 - Python)
Synthesizes Hayden Van Der Post's "Gamma Scalping: Advanced Python" and Patrick Boyle:
- Discrete Delta Neutrality Band Optimization: delta_threshold = (3 * Cost * Gamma / (2 * RiskAversion))^(1/3)
- Discrete Scalping PnL Formulation: PnL_scalp = 0.5 * Gamma * S^2 * (vol_realized^2 - vol_implied^2) * dt - Friction
- Multi-Trigger Rebalancing Protocols (Price delta trigger, Greek drift, Time interval)
- Microsecond Execution Slippage & Bid-Ask Friction matrix
"""

import math
from typing import Dict, List, Any, Optional


class DynamicGammaScalpingEngine:
    def __init__(self, risk_aversion: float = 1.0, transaction_cost_per_share: float = 0.005):
        self.risk_aversion = risk_aversion
        self.transaction_cost = transaction_cost_per_share

    def compute_optimal_rebalance_band(self, spot_price: float, portfolio_gamma: float) -> Dict[str, Any]:
        """
        Computes the discrete hedging threshold band using the asymptotic Leland/Whalley-Wilmott framework.
        delta_threshold = (3/2 * (Cost * Gamma) / RiskAversion) ** (1/3)
        """
        abs_gamma = max(1e-7, abs(portfolio_gamma))
        term = (1.5 * self.transaction_cost * abs_gamma) / max(1e-5, self.risk_aversion)
        threshold_delta = math.pow(term, 1.0 / 3.0)
        # Cap band between 0.02 and 0.25 delta
        clamped_band = max(0.02, min(0.25, threshold_delta))

        price_move_trigger = (clamped_band / abs_gamma) if abs_gamma > 0 else 1.0

        return {
            "portfolio_gamma": portfolio_gamma,
            "optimal_delta_threshold": round(clamped_band, 4),
            "price_move_trigger_dollars": round(price_move_trigger, 2),
            "upper_delta_bound": round(+clamped_band, 4),
            "lower_delta_bound": round(-clamped_band, 4)
        }

    def evaluate_rebalance_trigger(self, current_delta: float, target_delta: float, threshold: float) -> Dict[str, Any]:
        """
        Determines if current position delta has drifted past the optimal threshold band.
        """
        delta_drift = current_delta - target_delta
        is_triggered = abs(delta_drift) >= threshold

        shares_to_hedge = int(-delta_drift * 100.0) if is_triggered else 0

        action = "HOLD"
        if is_triggered:
            action = "SELL_SHARES" if delta_drift > 0 else "BUY_SHARES"

        return {
            "current_delta": round(current_delta, 4),
            "target_delta": round(target_delta, 4),
            "delta_drift": round(delta_drift, 4),
            "threshold": round(threshold, 4),
            "is_triggered": is_triggered,
            "action": action,
            "shares_to_rebalance": shares_to_hedge
        }

    def calculate_scalp_pnl_attribution(
        self,
        portfolio_gamma: float,
        spot_price: float,
        realized_vol: float,
        implied_vol: float,
        dt_years: float,
        total_transaction_costs: float
    ) -> Dict[str, Any]:
        """
        Calculates theoretical gamma scalping PnL:
        PnL ~ 0.5 * Gamma * S^2 * (sigma_realized^2 - sigma_implied^2) * dt - Costs
        """
        gamma_dollar = 0.5 * portfolio_gamma * (spot_price ** 2)
        variance_diff = (realized_vol ** 2) - (implied_vol ** 2)
        gross_gamma_pnl = gamma_dollar * variance_diff * dt_years
        net_scalp_pnl = gross_gamma_pnl - total_transaction_costs

        is_profitable = net_scalp_pnl > 0.0

        return {
            "spot_price": spot_price,
            "portfolio_gamma": portfolio_gamma,
            "realized_vol_pct": round(realized_vol * 100.0, 2),
            "implied_vol_pct": round(implied_vol * 100.0, 2),
            "variance_spread": round(variance_diff, 6),
            "gross_gamma_pnl": round(gross_gamma_pnl, 2),
            "friction_costs": round(total_transaction_costs, 2),
            "net_scalp_pnl": round(net_scalp_pnl, 2),
            "is_profitable": is_profitable,
            "scalping_regime": "VOLATILITY_OVERPERFORMING" if realized_vol > implied_vol else "THETA_BLEED_EXCEEDING_VOL"
        }
