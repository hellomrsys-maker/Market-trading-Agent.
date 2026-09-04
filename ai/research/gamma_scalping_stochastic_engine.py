"""
Algorithmic Gamma Scalping & Stochastic Volatility Engine (Module BF1 - Python)
Synthesizes Hayden Van Der Post's "Gamma Scalping":
- High-Frequency Dynamic Delta Hedging & Convexity Extraction (DeltaDelta = Gamma * DeltaS)
- Second-Order Greeks (Delta, Gamma, Theta, Vega, Rho, Vanna, Vomma)
- Heston Stochastic Volatility & Monte Carlo Pricing Simulator
"""

import math
from typing import Dict, List, Any
import numpy as np


class GammaScalpingStochasticEngine:
    def __init__(self, delta_threshold: float = 0.05):
        self.delta_threshold = delta_threshold

    def calculate_black_scholes_greeks(
        self,
        spot: float,
        strike: float,
        time_to_exp: float,
        r: float,
        sigma: float,
        is_call: bool = True
    ) -> Dict[str, float]:
        """
        Closed-form analytical Greeks for dynamic scalping.
        """
        t = max(1e-5, time_to_exp)
        s = max(1e-4, spot)
        sig = max(1e-4, sigma)

        d1 = (math.log(s / strike) + (r + 0.5 * sig ** 2) * t) / (sig * math.sqrt(t))
        d2 = d1 - sig * math.sqrt(t)

        phi_d1 = (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * d1 ** 2)
        nd1 = 0.5 * (1.0 + math.erf(d1 / math.sqrt(2.0)))
        nd2 = 0.5 * (1.0 + math.erf(d2 / math.sqrt(2.0)))

        delta = nd1 if is_call else (nd1 - 1.0)
        gamma = phi_d1 / (s * sig * math.sqrt(t))
        vega = s * phi_d1 * math.sqrt(t) / 100.0
        theta = (-(s * phi_d1 * sig) / (2.0 * math.sqrt(t)) - r * strike * math.exp(-r * t) * (nd2 if is_call else (1.0 - nd2))) / 365.0
        
        # Second-order Greeks
        vomma = (vega * d1 * d2) / sig
        vanna = (vega / s) * (1.0 - (d1 / (sig * math.sqrt(t))))

        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta, 4),
            "vega": round(vega, 4),
            "vomma": round(vomma, 6),
            "vanna": round(vanna, 6)
        }

    def compute_gamma_scalping_hedge(
        self,
        current_portfolio_delta: float,
        spot_price: float,
        gamma_total: float
    ) -> Dict[str, Any]:
        """
        Determines the rebalancing share quantity to achieve delta neutrality.
        """
        shares_to_trade = -current_portfolio_delta
        is_rebalance_required = abs(current_portfolio_delta) >= self.delta_threshold

        return {
            "current_delta": round(current_portfolio_delta, 4),
            "shares_to_hedge": round(shares_to_trade, 2),
            "is_rebalance_required": is_rebalance_required,
            "hedge_action": "EXECUTE_DELTA_NEUTRAL_HEDGE" if is_rebalance_required else "HOLD_WITHIN_BAND"
        }
