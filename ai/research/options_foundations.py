r"""
ai/research/options_foundations.py
===================================
OptionAlpha Agent — Core Mathematical Foundations of Options & Polyglot Engine Specification

Provides exhaustive, verbatim mathematical models and specifications for:
  1. Call Option: The financial derivative giving the holder the right (not obligation)
     to purchase 100 shares of the underlying asset at strike price $K$ on or before expiration $T$.
     Payoff: $\max(S_T - K, 0) - C_0$ (Long) or $C_0 - \max(S_T - K, 0)$ (Short).
  2. Put Option: The financial derivative giving the holder the right (not obligation)
     to sell 100 shares of the underlying asset at strike price $K$ on or before expiration $T$.
     Payoff: $\max(K - S_T, 0) - P_0$ (Long) or $P_0 - \max(K - S_T, 0)$ (Short).
  3. Contract Multiplier: 100 shares per standard US equity contract.
     Dollar Exposure = Price * Multiplier * Qty.
  4. Premium: Upfront price composed of Intrinsic Value + Extrinsic (Time + Volatility) Value.
  5. 6-Pillar Polyglot Implementation Mapping:
     - Rust: SIMD contract multiplier scaling & tick order processing
     - Julia: SVI local volatility surface, Dupire PDE & closed-form BSM
     - C++: Zero-Bridge 64-byte AtomicStateVector (0-ns synchronisation)
     - CUDA/Triton: GPU batched parallel Monte Carlo pricing paths
     - Java: Prometheus metrics export of contract exposure
     - Python: High-level cognitive training & execution API
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy.stats import norm
from loguru import logger


@dataclass
class OptionContractSpecification:
    """
    Standardized Options Contract Model (US Equity Option Standard).
    """
    symbol: str
    underlying: str
    option_type: str             # "CALL" | "PUT"
    strike_price: float          # K
    expiration_years: float      # T in years
    spot_price: float            # S
    risk_free_rate: float        # r (annualized)
    implied_volatility: float    # sigma
    multiplier: int = 100        # Standard 100 shares per contract

    @property
    def intrinsic_value(self) -> float:
        """Intrinsic Value per share."""
        if self.option_type.upper() == "CALL":
            return max(0.0, self.spot_price - self.strike_price)
        else:
            return max(0.0, self.strike_price - self.spot_price)

    @property
    def total_contract_multiplier(self) -> int:
        return self.multiplier

    def compute_bsm_analytical(self) -> Dict[str, float]:
        """
        Analytical Black-Scholes-Merton Pricing & Higher-Order Greeks.
        """
        S = self.spot_price
        K = self.strike_price
        T = max(1e-5, self.expiration_years)
        r = self.risk_free_rate
        sigma = max(1e-4, self.implied_volatility)

        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        n_d1 = float(norm.pdf(d1))
        N_d1 = float(norm.cdf(d1))
        N_d2 = float(norm.cdf(d2))
        N_minus_d1 = float(norm.cdf(-d1))
        N_minus_d2 = float(norm.cdf(-d2))

        discount = math.exp(-r * T)

        if self.option_type.upper() == "CALL":
            price = S * N_d1 - K * discount * N_d2
            delta = N_d1
            theta = -(S * n_d1 * sigma) / (2 * math.sqrt(T)) - r * K * discount * N_d2
            rho = K * T * discount * N_d2
        else:
            price = K * discount * N_minus_d2 - S * N_minus_d1
            delta = N_d1 - 1.0
            theta = -(S * n_d1 * sigma) / (2 * math.sqrt(T)) + r * K * discount * N_minus_d2
            rho = -K * T * discount * N_minus_d2

        gamma = n_d1 / (S * sigma * math.sqrt(T))
        vega = S * math.sqrt(T) * n_d1 * 0.01  # per 1% vol change

        # Higher-Order Greeks (Vanna, Charm, Volga)
        vanna = -n_d1 * (d2 / sigma) * 0.01
        volga = vega * (d1 * d2 / sigma) * 0.01
        charm = -n_d1 * (2 * r * T - d2 * sigma * math.sqrt(T)) / (2 * T * sigma * math.sqrt(T))

        extrinsic_value = max(0.0, price - self.intrinsic_value)

        return {
            "theoretical_price": round(price, 4),
            "intrinsic_value": round(self.intrinsic_value, 4),
            "extrinsic_value": round(extrinsic_value, 4),
            "contract_dollar_premium": round(price * self.multiplier, 2),
            "contract_notional_value": round(S * self.multiplier, 2),
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta_per_day": round(theta / 365.0, 4),
            "vega": round(vega, 4),
            "rho": round(rho * 0.01, 4),
            "vanna": round(vanna, 6),
            "volga": round(volga, 6),
            "charm": round(charm, 6),
        }

    def compute_payoff_at_expiration(self, terminal_spot: float, position_side: str = "LONG") -> float:
        """
        Computes exact contract P&L at expiration across the underlying terminal price curve.
        """
        unit_payoff = 0.0
        if self.option_type.upper() == "CALL":
            unit_payoff = max(0.0, terminal_spot - self.strike_price)
        else:
            unit_payoff = max(0.0, self.strike_price - terminal_spot)

        bsm = self.compute_bsm_analytical()
        entry_premium = bsm["theoretical_price"]

        if position_side.upper() == "LONG":
            net_unit_pnl = unit_payoff - entry_premium
        else:  # SHORT
            net_unit_pnl = entry_premium - unit_payoff

        return round(net_unit_pnl * self.multiplier, 2)
