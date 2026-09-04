"""
ai/research/dispersion_rainbow_engine.py
========================================
OptionAlpha Agent — Module U1: Python Multi-Asset Dispersion, Rainbow & Basket Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Tuple
from scipy.stats import norm

class DispersionRainbowEngine:
    """
    Synthesizes 'Exotic Options and Hybrids' (Bouzoubaa & Osseiran) - Part II:
    - Realized & Implied Correlation Matrices, Correlation Skew
    - Best-of & Worst-of Options (Stulz 1995 & Parity: BO + WO = C1 + C2)
    - Rainbow Options (Weighted ranked performance)
    - Individually Capped Basket Calls (ICBC) vs Capped Basket Calls (CBC)
    - Margrabe (1978) Outperformance Spread Options
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    @staticmethod
    def calculate_basket_variance(
        weights: np.ndarray,
        volatilities: np.ndarray,
        corr_matrix: np.ndarray
    ) -> float:
        """
        Calculates Portfolio/Basket Variance:
        sigma_p^2 = sum(w_i^2 * sigma_i^2) + 2 * sum_{i < j}(w_i * w_j * sigma_i * sigma_j * rho_ij)
        """
        w = np.array(weights, dtype=np.float64)
        v = np.array(volatilities, dtype=np.float64)
        cov_matrix = np.outer(v, v) * corr_matrix
        var_p = float(w.T @ cov_matrix @ w)
        return max(1e-6, var_p)

    @staticmethod
    def calculate_worst_of_best_of_parity(
        call_s1: float,
        call_s2: float,
        worst_of_call: float
    ) -> float:
        """
        Best-of / Worst-of Call Parity:
        BO_call(K) + WO_call(K) = C(S1, K) + C(S2, K)
        => BO_call(K) = C(S1, K) + C(S2, K) - WO_call(K)
        """
        return call_s1 + call_s2 - worst_of_call

    @staticmethod
    def calculate_rainbow_payoff(
        returns: List[float],
        weights_descending: List[float]
    ) -> float:
        """
        Rainbow Option Payoff:
        Ranks individual asset returns and assigns descending weights
        (e.g., 50% Best + 30% Second + 20% Third)
        """
        sorted_rets = sorted(returns, reverse=True)
        payoff = sum(w * r for w, r in zip(weights_descending, sorted_rets))
        return max(0.0, float(payoff))

    @staticmethod
    def evaluate_icbc_vs_cbc(
        individual_returns: List[float],
        cap: float
    ) -> Dict[str, float]:
        """
        ICBC Payoff = max[0, 1/N * sum(min(Ret_i, Cap))]
        CBC Payoff  = max[0, min(1/N * sum(Ret_i), Cap)]
        Always satisfies: ICBC_payoff <= CBC_payoff
        """
        n = len(individual_returns)
        icbc = max(0.0, sum(min(r, cap) for r in individual_returns) / n)
        cbc = max(0.0, min(sum(individual_returns) / n, cap))
        return {
            "icbc_payoff": icbc,
            "cbc_payoff": cbc,
            "dispersion_benefit": cbc - icbc
        }

    @staticmethod
    def calculate_margrabe_outperformance(
        s1: float, s2: float,
        t_years: float,
        sigma1: float, sigma2: float,
        rho: float,
        q1: float = 0.0, q2: float = 0.0
    ) -> float:
        """
        Margrabe (1978) Option to Exchange S2 for S1:
        Price = S1*e^(-q1*T)*N(d1) - S2*e^(-q2*T)*N(d2)
        where sigma_hat = sqrt(sigma1^2 + sigma2^2 - 2*rho*sigma1*sigma2)
        """
        if t_years <= 0 or s1 <= 0 or s2 <= 0:
            return max(0.0, s1 - s2)
            
        sigma_hat = math.sqrt(max(1e-6, sigma1**2 + sigma2**2 - 2.0 * rho * sigma1 * sigma2))
        sqrt_t = math.sqrt(t_years)
        
        d1 = (math.log(s1 / s2) + (q2 - q1 + 0.5 * sigma_hat**2) * t_years) / (sigma_hat * sqrt_t)
        d2 = d1 - sigma_hat * sqrt_t
        
        call_val = s1 * math.exp(-q1 * t_years) * norm.cdf(d1) - s2 * math.exp(-q2 * t_years) * norm.cdf(d2)
        return max(0.0, float(call_val))
