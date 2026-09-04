"""
Higher-Order Greeks, Moments & Volatility Surface Engine (Module AD1 - Python)
Synthesizes the Greek dynamics and volatility surface models of Tony Saliba (Managing Expectations):
- First-Order Greeks (Delta, Gamma, Vega, Theta, Rho) with Time & Volatility convergence behavior
- Second-Order Greeks: Vanna, Vomma (Volga), Charm (Delta Bleed)
- 4 Moments of Probability Distribution (Mean, Variance, Skewness, Kurtosis)
- Forward Implied Volatility Calculus & Volatility Cone Analysis
- Term Structure Dynamics (Normal Contango vs Inverted Backwardation)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math
import numpy as np


@dataclass
class GreeksProfile:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    vanna: float
    vomma: float
    charm: float
    theta_vega_ratio: float


class SecondOrderGreeksSurfaceEngine:
    """
    Module AD1: Higher-Order Greeks, Moments & Volatility Surface Engine.
    Calculates analytical first- and second-order Greeks, forward implied volatility, and skew dynamics.
    """

    def __init__(self):
        pass

    def _std_norm_pdf(self, x: float) -> float:
        return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

    def _std_norm_cdf(self, x: float) -> float:
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def calculate_full_greeks(
        self,
        spot: float,
        strike: float,
        volatility: float,
        time_to_exp_years: float,
        risk_free_rate: float,
        dividend_yield: float = 0.0,
        is_call: bool = True
    ) -> GreeksProfile:
        """
        Computes Black-Scholes 1st and 2nd Order Greeks including Vanna, Vomma, and Charm.
        """
        s = max(0.01, spot)
        k = max(0.01, strike)
        sigma = max(0.001, volatility)
        t = max(0.0001, time_to_exp_years)
        r = risk_free_rate
        q = dividend_yield

        sqrt_t = math.sqrt(t)
        d1 = (math.log(s / k) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t)
        d2 = d1 - sigma * sqrt_t

        n_d1 = self._std_norm_cdf(d1)
        n_d2 = self._std_norm_cdf(d2)
        n_minus_d1 = self._std_norm_cdf(-d1)
        n_minus_d2 = self._std_norm_cdf(-d2)
        phi_d1 = self._std_norm_pdf(d1)

        # 1st Order Greeks
        if is_call:
            delta = math.exp(-q * t) * n_d1
            rho = k * t * math.exp(-r * t) * n_d2 / 100.0
            theta = (- (s * sigma * math.exp(-q * t) * phi_d1) / (2.0 * sqrt_t)
                     - r * k * math.exp(-r * t) * n_d2
                     + q * s * math.exp(-q * t) * n_d1) / 365.0
        else:
            delta = -math.exp(-q * t) * n_minus_d1
            rho = -k * t * math.exp(-r * t) * n_minus_d2 / 100.0
            theta = (- (s * sigma * math.exp(-q * t) * phi_d1) / (2.0 * sqrt_t)
                     + r * k * math.exp(-r * t) * n_minus_d2
                     - q * s * math.exp(-q * t) * n_minus_d1) / 365.0

        gamma = (math.exp(-q * t) * phi_d1) / (s * sigma * sqrt_t)
        vega = (s * math.exp(-q * t) * phi_d1 * sqrt_t) / 100.0  # 1% move

        # 2nd Order Greeks
        # Vanna: dDelta / dSigma = dVega / dSpot
        vanna = (-math.exp(-q * t) * phi_d1 * d2 / sigma) / 100.0
        # Vomma: dVega / dSigma = Vega * (d1 * d2 / sigma)
        vomma = (vega * (d1 * d2 / sigma)) / 100.0
        # Charm: dDelta / dTime (Delta Bleed)
        charm = (-math.exp(-q * t) * phi_d1 * (2.0 * (r - q) * t - d2 * sigma * sqrt_t) / (2.0 * t * sigma * sqrt_t)) / 365.0
        if not is_call:
            charm = charm + (q * math.exp(-q * t) * n_minus_d1) / 365.0

        theta_vega = abs(theta / vega) if vega > 0 else 0.0

        return GreeksProfile(
            delta=round(delta, 4),
            gamma=round(gamma, 6),
            vega=round(vega, 4),
            theta=round(theta, 4),
            rho=round(rho, 4),
            vanna=round(vanna, 6),
            vomma=round(vomma, 6),
            charm=round(charm, 6),
            theta_vega_ratio=round(theta_vega, 4)
        )

    def calculate_forward_implied_volatility(
        self,
        vol_near: float,
        days_near: int,
        vol_deferred: float,
        days_deferred: int
    ) -> float:
        """
        Calculates the forward implied volatility between near and deferred maturities:
        sigma_fwd = sqrt( (sigma_2^2 * days_2 - sigma_1^2 * days_1) / (days_2 - days_1) )
        """
        if days_deferred <= days_near:
            return vol_deferred

        v1_sq_t = (vol_near ** 2) * days_near
        v2_sq_t = (vol_deferred ** 2) * days_deferred
        delta_t = days_deferred - days_near

        numerator = v2_sq_t - v1_sq_t
        if numerator <= 0:
            return 0.0

        fwd_vol = math.sqrt(numerator / delta_t)
        return round(fwd_vol, 4)

    def evaluate_volatility_term_structure(
        self,
        expirations_days: List[int],
        implied_vols: List[float]
    ) -> Dict[str, Any]:
        """
        Determines term structure slope regime (Contango vs Backwardation).
        """
        if len(expirations_days) < 2:
            return {"regime": "FLAT", "slope": 0.0}

        slope = (implied_vols[-1] - implied_vols[0]) / float(expirations_days[-1] - expirations_days[0])
        if slope > 0.0005:
            regime = "NORMAL_CONTANGO"
        elif slope < -0.0005:
            regime = "INVERTED_BACKWARDATION"
        else:
            regime = "FLAT"

        return {
            "regime": regime,
            "slope_per_day": round(slope, 6),
            "front_month_vol": implied_vols[0],
            "back_month_vol": implied_vols[-1]
        }
