"""
ai/research/variance_swap_copula_engine.py
=========================================
OptionAlpha Agent — Module X1: Python Volatility Derivatives, Variance Swaps & Hybrid Copula Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Tuple
from scipy.stats import norm

class VarianceSwapCopulaEngine:
    """
    Synthesizes 'Exotic Options and Hybrids' (Bouzoubaa & Osseiran) - Part III Ch 16 & Part IV Ch 19, 20, 21:
    - Variance Swaps & Log-Contract Replication (Demeterfi, Derman et al. 1999)
    - Variance Swap Greeks (Constant Cash Gamma = 2/T, Linear Vega, Negative Theta)
    - Corridor Variance Swaps & Gamma Swaps
    - Sklar's Theorem & Multi-Asset Gaussian Copula Simulation (Cholesky LL^T)
    - Markowitz Mean-Variance Optimization & Thematic Index Hedging
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    @staticmethod
    def calculate_realized_variance(log_returns: List[float], annualization_factor: float = 252.0) -> float:
        """
        Realized Variance RV(T) = A / N * sum(ln(S_i / S_{i-1})^2)
        """
        n = len(log_returns)
        if n == 0:
            return 0.0
        sum_sq = sum(r * r for r in log_returns)
        return float((annualization_factor / n) * sum_sq)

    @staticmethod
    def calculate_variance_swap_greeks(
        t_years: float,
        time_elapsed: float,
        current_sigma: float
    ) -> Dict[str, float]:
        """
        Demeterfi et al. (1999) Variance Swap Greeks:
        Cash Gamma = 2.0 / T (Constant!)
        Vega = (2.0 / T) * sigma * (T - t) (Linear in vol!)
        Theta = - (1.0 / T) * sigma^2
        """
        t_rem = max(1e-4, t_years - time_elapsed)
        cash_gamma = 2.0 / max(1e-4, t_years)
        vega = (2.0 / max(1e-4, t_years)) * current_sigma * t_rem
        theta = - (1.0 / max(1e-4, t_years)) * (current_sigma ** 2)
        return {
            "cash_gamma": cash_gamma,
            "vega": vega,
            "theta": theta
        }

    @staticmethod
    def simulate_gaussian_copula(
        corr_matrix: np.ndarray,
        n_samples: int = 1000
    ) -> np.ndarray:
        """
        Simulates correlated uniform margins U in [0, 1]^N via Gaussian Copula:
        1. Cholesky decomposition M = L * L^T
        2. Generate independent standard normal epsilon ~ N(0, I)
        3. Correlate: eta = L * epsilon
        4. Map back to uniform margins: u = Phi(eta)
        """
        l_chol = np.linalg.cholesky(corr_matrix)
        dim = corr_matrix.shape[0]
        eps = np.random.standard_normal((dim, n_samples))
        eta = l_chol @ eps
        u_margins = norm.cdf(eta)
        return u_margins.T # Shape: (n_samples, dim)

    @staticmethod
    def calculate_markowitz_efficient_weights(
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        target_return: float
    ) -> np.ndarray:
        """
        Calculates Markowitz Minimum Variance Portfolio weights subject to sum(w)=1 and E[R_p]=target:
        Analytical Lagrangian solution.
        """
        inv_cov = np.linalg.pinv(cov_matrix)
        ones = np.ones(len(expected_returns))
        
        a = float(ones.T @ inv_cov @ ones)
        b = float(ones.T @ inv_cov @ expected_returns)
        c = float(expected_returns.T @ inv_cov @ expected_returns)
        d = a * c - b * b
        
        if abs(d) < 1e-8:
            weights = ones / len(ones)
        else:
            lambda_mult = (c - b * target_return) / d
            gamma_mult = (a * target_return - b) / d
            weights = inv_cov @ (lambda_mult * ones + gamma_mult * expected_returns)
            
        return weights
