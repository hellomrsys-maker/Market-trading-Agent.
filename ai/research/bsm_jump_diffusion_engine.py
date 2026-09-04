"""
ai/research/bsm_jump_diffusion_engine.py
========================================
OptionAlpha Agent — Module R1: Python Advanced Black-Scholes, Greeks & Jump-Diffusion Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Tuple
from scipy.stats import norm

class BSMJumpDiffusionEngine:
    """
    Synthesizes 'Basic Black-Scholes: Option Pricing and Trading' (Timothy Falcon Crack):
    - Merton Continuous Dividend Formula & Garman-Kohlhagen FX Options
    - Put-Call Parity & Regrets Decompositions
    - Stock vs Bond Numeraire Equivalent Martingale Measures (N(d1) vs N(d2))
    - First-Passage Probability of Ever Being ITM (P*_ever(ITM))
    - Merton Jump-Diffusion Model & Power Options
    - Option Elasticity (Implicit Leverage / Multiplicative Factor)
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    @staticmethod
    def calculate_bsm_merton(
        s: float, x: float, t_years: float, r: float, sigma: float, q_div: float = 0.0
    ) -> Dict[str, float]:
        """
        Black-Scholes-Merton with continuous dividend yield q_div:
        c = S*e^(-q*T)*N(d1) - X*e^(-r*T)*N(d2)
        p = X*e^(-r*T)*N(-d2) - S*e^(-q*T)*N(-d1)
        """
        if t_years <= 0 or sigma <= 0 or s <= 0 or x <= 0:
            call_val = max(0.0, s - x)
            put_val = max(0.0, x - s)
            return {
                "call_price": call_val, "put_price": put_val,
                "d1": 0.0, "d2": 0.0, "delta_call": 1.0 if s > x else 0.0,
                "delta_put": -1.0 if s < x else 0.0, "gamma": 0.0,
                "theta_call": 0.0, "vega": 0.0, "elasticity_call": 1.0
            }

        sqrt_t = math.sqrt(t_years)
        d1 = (math.log(s / x) + (r - q_div + 0.5 * sigma * sigma) * t_years) / (sigma * sqrt_t)
        d2 = d1 - sigma * sqrt_t

        n_d1 = norm.cdf(d1)
        n_d2 = norm.cdf(d2)
        n_minus_d1 = norm.cdf(-d1)
        n_minus_d2 = norm.cdf(-d2)
        phi_d1 = norm.pdf(d1)

        exp_qt = math.exp(-q_div * t_years)
        exp_rt = math.exp(-r * t_years)

        call_price = s * exp_qt * n_d1 - x * exp_rt * n_d2
        put_price = x * exp_rt * n_minus_d2 - s * exp_qt * n_minus_d1

        delta_call = exp_qt * n_d1
        delta_put = -exp_qt * n_minus_d1
        gamma = (exp_qt * phi_d1) / (s * sigma * sqrt_t)
        vega = s * exp_qt * phi_d1 * sqrt_t
        theta_call = (- (s * sigma * exp_qt * phi_d1) / (2.0 * sqrt_t) 
                      - r * x * exp_rt * n_d2 + q_div * s * exp_qt * n_d1) / 365.0

        elasticity_call = (s * delta_call) / max(1e-4, call_price)

        return {
            "call_price": call_price,
            "put_price": put_price,
            "d1": d1,
            "d2": d2,
            "delta_call": delta_call,
            "delta_put": delta_put,
            "gamma": gamma,
            "theta_call": theta_call,
            "vega": vega,
            "elasticity_call": elasticity_call
        }

    @staticmethod
    def calculate_regrets_decomposition(
        s: float, x: float, t_years: float, r: float, put_price: float
    ) -> Dict[str, float]:
        """
        Put-Call Parity Regrets Decomposition (Crack Eq 3.8):
        C = [S - X] + [X - X*e^(-r*T)] + p
        Components:
        1. Exercise Value: S - X
        2. Delaying Exercise (Interest on Strike): X - X*e^(-r*T)
        3. Implicit Downside Insurance Put: p
        """
        exercise_val = s - x
        interest_on_strike = x * (1.0 - math.exp(-r * t_years))
        insurance_put = put_price
        total_call_value = exercise_val + interest_on_strike + insurance_put

        return {
            "exercise_value": exercise_val,
            "interest_on_strike": interest_on_strike,
            "insurance_put": insurance_put,
            "decomposed_call_value": total_call_value
        }

    @staticmethod
    def calculate_probability_ever_itm(
        s: float, x: float, t_years: float, r: float, sigma: float, q_div: float = 0.0
    ) -> float:
        """
        Risk-Neutral Probability that the Call is EVER In-The-Money (Crack Eq 8.41):
        P*_ever(ITM) = N(d2) + e^(2ab) * N(d2 - 2a*sqrt(T))
        where b = 1/sigma * ln(X/S), a = 1/sigma * (r - q - 0.5*sigma^2)
        """
        if s >= x:
            return 1.0
        if t_years <= 0 or sigma <= 0:
            return 0.0

        sqrt_t = math.sqrt(t_years)
        d2 = (math.log(s / x) + (r - q_div - 0.5 * sigma * sigma) * t_years) / (sigma * sqrt_t)
        b = (1.0 / sigma) * math.log(x / s)
        a = (1.0 / sigma) * (r - q_div - 0.5 * sigma * sigma)

        p_ever = norm.cdf(d2) + math.exp(2.0 * a * b) * norm.cdf(d2 - 2.0 * a * sqrt_t)
        return min(1.0, max(0.0, float(p_ever)))

    @staticmethod
    def calculate_merton_jump_diffusion(
        s: float, x: float, t_years: float, r: float, sigma: float,
        lambda_jumps: float, gamma_mean: float, delta_vol: float, n_terms: int = 15
    ) -> float:
        """
        Merton (1976) Jump Diffusion Option Price (Poisson Jumps):
        c = sum_{n=0}^{N} [ e^(-lambda'*T) * (lambda'*T)^n / n! ] * BSM(S, X, T, r_n, sigma_n)
        where lambda' = lambda_jumps * (1 + k), k = exp(gamma + delta^2/2) - 1
        """
        k = math.exp(gamma_mean + 0.5 * delta_vol * delta_vol) - 1.0
        lambda_prime = lambda_jumps * (1.0 + k)

        call_price = 0.0
        for n in range(n_terms):
            r_n = r - lambda_jumps * k + (n * math.log(1.0 + k)) / max(1e-4, t_years)
            sigma_n = math.sqrt(sigma * sigma + (n * delta_vol * delta_vol) / max(1e-4, t_years))
            poisson_prob = (math.exp(-lambda_prime * t_years) * ((lambda_prime * t_years) ** n)) / math.factorial(n)
            
            d1_n = (math.log(s / x) + (r_n + 0.5 * sigma_n * sigma_n) * t_years) / (sigma_n * math.sqrt(t_years))
            d2_n = d1_n - sigma_n * math.sqrt(t_years)
            bsm_n = s * norm.cdf(d1_n) - x * math.exp(-r_n * t_years) * norm.cdf(d2_n)
            
            call_price += poisson_prob * bsm_n

        return call_price
