"""
Institutional Volatility Edge & Expiration Microstructure Engine (Module AI1 - Python)
Synthesizes Jeff Augen's "Volatility Edge in Options Trading", "Trading Options at Expiration"
and Mark Sebastian's "The Option Trader's Hedge Fund":
- Expiration Day Pinning Gravitational Field & Zero-DTE Gamma Acceleration
- Day-of-Week Volatility Decay Anomaly (Accelerated Thursday/Friday Theta)
- Intraday Volatility Velocity & Spike Return Metrics (dIV / dt)
- Vega/Theta Portfolio Efficiency Ratio (|Vega| / |Theta|)
- Probability of Touch vs. Probability of Expiring ITM: P_touch ~ 2 * N(-d2) vs P_ITM = N(d2)
"""

import math
from typing import Dict, List, Any


class VolatilityEdgeExpirationEngine:
    def __init__(self, vega_theta_max_ratio: float = 3.5):
        self.vega_theta_max_ratio = vega_theta_max_ratio

    def calculate_pinning_force(self, spot_price: float, strike_price: float, dte_days: float, open_interest_contracts: int) -> Dict[str, Any]:
        """
        Models expiration day pinning gravitational force towards max OI strike.
        Gravitational Force ~ OpenInterest / (Distance^2 + epsilon) * exp(-DTE)
        """
        distance = abs(spot_price - strike_price)
        time_factor = math.exp(-max(0.01, dte_days) * 2.0)
        gravitational_pull = (open_interest_contracts / (distance ** 2 + 1.0)) * time_factor

        is_high_pin_risk = (distance < 2.0) and (dte_days <= 1.0) and (open_interest_contracts > 5000)

        return {
            "spot_price": spot_price,
            "strike_price": strike_price,
            "distance": round(distance, 2),
            "dte_days": dte_days,
            "pinning_pull_score": round(gravitational_pull, 2),
            "is_pinning_candidate": is_high_pin_risk,
            "trade_recommendation": "EXPLOIT_BUTTERFLY_OR_IRON_CONDOR_PIN" if is_high_pin_risk else "STANDARD_SPREAD"
        }

    def evaluate_vega_theta_budget(self, portfolio_vega: float, portfolio_theta: float) -> Dict[str, Any]:
        """
        Calculates Vega-to-Theta risk ratio.
        Mark Sebastian Rule: Keep |Vega| / |Theta| within reasonable boundaries to avoid uncompensated vol risk.
        """
        abs_vega = abs(portfolio_vega)
        abs_theta = max(1e-4, abs(portfolio_theta))
        ratio = abs_vega / abs_theta

        is_risk_balanced = ratio <= self.vega_theta_max_ratio

        if ratio > self.vega_theta_max_ratio:
            status = "VEGA_OVEREXPOSED_EXCESSIVE_VOL_RISK"
            adjustment = "ADD_SHORT_VEGA_OR_INCREASE_THETA_DECAY_COLLECTION"
        elif ratio < 0.5:
            status = "THETA_DOMINATED_SHORT_VOL_SQUEEZE_RISK"
            adjustment = "ADD_LONG_VEGA_TAIL_HEDGES"
        else:
            status = "OPTIMALLY_BALANCED_PORTFOLIO"
            adjustment = "MAINTAIN_CURRENT_GREEK_PROFILE"

        return {
            "portfolio_vega": round(portfolio_vega, 2),
            "portfolio_theta": round(portfolio_theta, 2),
            "vega_theta_ratio": round(ratio, 2),
            "max_allowed_ratio": self.vega_theta_max_ratio,
            "is_balanced": is_risk_balanced,
            "status": status,
            "adjustment_protocol": adjustment
        }

    def compute_touch_vs_expiration_probability(self, spot_price: float, strike_price: float, iv: float, dte_days: float) -> Dict[str, Any]:
        """
        Calculates Probability of Touch vs Probability of Expiring ITM.
        P_ITM = N(d2), P_touch ~ 2 * N(d2) (for OTM options)
        """
        t = max(1e-4, dte_days / 365.0)
        sigma_sqrt_t = iv * math.sqrt(t)
        
        # d2 formula assuming r=0 for approximation
        d2 = (math.log(spot_price / strike_price) - 0.5 * (iv ** 2) * t) / sigma_sqrt_t

        def norm_cdf(x):
            return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

        # For OTM Call (Strike > Spot) or OTM Put (Strike < Spot)
        if strike_price >= spot_price:
            prob_itm = norm_cdf(d2)
            prob_touch = min(0.999, 2.0 * prob_itm)
        else:
            prob_itm = norm_cdf(-d2)
            prob_touch = min(0.999, 2.0 * prob_itm)

        return {
            "spot_price": spot_price,
            "strike_price": strike_price,
            "dte_days": dte_days,
            "prob_expiring_itm_pct": round(prob_itm * 100.0, 2),
            "prob_touching_strike_pct": round(prob_touch * 100.0, 2),
            "touch_multiplier": round(prob_touch / max(1e-4, prob_itm), 2),
            "warning": "HIGH_TOUCH_RISK_DOUBLE_EXPIRATION_PROBABILITY" if prob_touch > 0.40 else "SAFE_BUFFER"
        }
