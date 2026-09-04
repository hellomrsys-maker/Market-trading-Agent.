"""
ai/research/barrier_autocallable_engine.py
=========================================
OptionAlpha Agent — Module V1: Python Barrier, Digital & Autocallable Structuring Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Tuple
from scipy.stats import norm

class BarrierAutocallableEngine:
    """
    Synthesizes 'Exotic Options and Hybrids' (Bouzoubaa & Osseiran) - Part II Chapters 10, 11, 12:
    - Continuous & Discrete Barrier Options (Broadie-Glasserman-Kou 1997 Shift)
    - European & American Digitals with Skew/Vega Correction
    - One-Touch vs No-Touch Parity
    - Single-Asset & Multi-Asset Autocallables, Twin-Wins & Snowball Structures
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    @staticmethod
    def calculate_discrete_barrier_shift(
        barrier: float,
        sigma: float,
        t_years: float,
        num_observations: int,
        is_short_barrier: bool
    ) -> float:
        """
        Broadie, Glasserman & Kou (1997) Discrete Monitoring Formula:
        H' = H * exp(+/- 0.5826 * sigma * sqrt(T / m))
        (+) if short barrier / (-) if long barrier
        """
        if num_observations <= 0:
            return barrier
        dt = t_years / float(num_observations)
        factor = 0.5826 * sigma * math.sqrt(dt)
        return barrier * math.exp(factor if is_short_barrier else -factor)

    @staticmethod
    def calculate_digital_with_skew_correction(
        s: float, x: float, t_years: float, r: float, sigma: float,
        skew_d_sigma_dk: float, q_div: float = 0.0
    ) -> Dict[str, float]:
        """
        Digital Price with Skew Correction:
        Digital(K) = - d(Call)/dK = e^(-rT)*N(d2) + Vega * Skew
        where Skew = abs(d(sigma)/dK)
        """
        sqrt_t = math.sqrt(max(1e-6, t_years))
        d1 = (math.log(s / x) + (r - q_div + 0.5 * sigma * sigma) * t_years) / (sigma * sqrt_t)
        d2 = d1 - sigma * sqrt_t

        exp_qt = math.exp(-q_div * t_years)
        exp_rt = math.exp(-r * t_years)
        phi_d1 = norm.pdf(d1)

        vega = s * exp_qt * phi_d1 * sqrt_t
        bs_digital = exp_rt * norm.cdf(d2)
        skew_adjustment = vega * abs(skew_d_sigma_dk)
        total_digital_price = bs_digital + skew_adjustment

        return {
            "bs_digital_price": bs_digital,
            "skew_adjustment": skew_adjustment,
            "skew_corrected_digital_price": total_digital_price
        }

    @staticmethod
    def evaluate_autocallable_step(
        current_perf: float,
        autocall_trigger: float,
        coupon_trigger: float,
        annual_coupon_pct: float,
        accumulated_coupons: float,
        is_snowball: bool
    ) -> Dict[str, float | bool | str]:
        """
        Autocallable / Snowball Coupon Evaluation:
        - If Perf >= AutocallTrigger: Autocall fired, pays Notional + Total Coupon
        - If Perf < AutocallTrigger and Perf >= CouponTrigger: Pays Coupon
        - Snowball: Adds all missed previous period coupons if triggered
        """
        is_autocalled = current_perf >= autocall_trigger
        coupon_paid = 0.0
        
        if is_autocalled:
            coupon_paid = accumulated_coupons + annual_coupon_pct if is_snowball else annual_coupon_pct
            action = "AUTOCALL_REDEEMED"
        elif current_perf >= coupon_trigger:
            coupon_paid = accumulated_coupons + annual_coupon_pct if is_snowball else annual_coupon_pct
            action = "COUPON_PAID_CONTINUES"
        else:
            action = "NO_COUPON_CONTINUES"

        return {
            "is_autocalled": is_autocalled,
            "coupon_paid": coupon_paid,
            "next_accumulated": 0.0 if (is_autocalled or coupon_paid > 0) else (accumulated_coupons + annual_coupon_pct),
            "status": action
        }
