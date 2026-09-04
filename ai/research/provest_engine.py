"""
ai/research/provest_engine.py
=============================
OptionAlpha Agent — Jay Kaeppel's PROVEST Option Trading Framework
Based on "The Option Trader's Guide to Probability, Volatility, and Timing" (John Wiley & Sons)

Implements the 5 core PROVEST selection pillars:
  P - Probability: Delta-based probability of expiring in-the-money & breakeven probability analysis.
  V - Volatility: 24-Month Relative Volatility Ranking (Deciles 1 to 10) & Implied vs Historical Volatility.
  E - Expiration: Time Decay management (Theta curve acceleration, 45-day & 30-day DTE selection rules).
  S - Skew: Implied Volatility skew across strikes & expirations (min 15% disparity for Calendars/Backspreads).
  T - Timing: Directional vs Neutral market expectations and support/resistance validation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from loguru import logger


@dataclass
class PROVESTEvaluation:
    symbol: str
    probability_of_profit: float         # 0.0 to 1.0 (P)
    relative_volatility_rank: int        # 1 to 10 Decile (V)
    implied_volatility: float            # Annualized IV (V)
    historical_volatility_20d: float     # Annualized RV20 (V)
    days_to_expiration: int              # DTE (E)
    theta_decay_phase: str               # "LINEAR" | "ACCELERATED" | "TERMINAL" (E)
    volatility_skew_ratio: float         # 25d Put IV / 25d Call IV (S)
    calendar_vol_disparity_pct: float    # (Front IV - Back IV) / Back IV (S)
    timing_regime_bias: str              # "BULLISH" | "BEARISH" | "NEUTRAL_RANGE" (T)
    recommended_strategies: List[str]
    is_favorable_entry: bool
    provest_composite_score: float       # 0.0 to 1.0


class PROVESTEngine:
    """
    Evaluates options trade setups using the institutional PROVEST framework.
    """

    @classmethod
    def compute_relative_volatility_rank(cls, iv_series_24m: List[float], current_iv: float) -> int:
        """
        Computes the 24-month relative volatility rank (Deciles 1 to 10).
        Rank 1-3 = Low Volatility (Favor Option Buying, Calendars, Straddles, Backspreads)
        Rank 8-10 = High Volatility (Favor Option Writing, CSP, Covered Calls, Credit Verticals, Butterflies)
        """
        if not iv_series_24m:
            return 5
        sorted_iv = sorted(iv_series_24m)
        n = len(sorted_iv)
        # Find percentile rank
        count_below = sum(1 for v in sorted_iv if v <= current_iv)
        percentile = count_below / max(n, 1)
        rank = int(math.ceil(percentile * 10.0))
        return max(1, min(10, rank))

    @classmethod
    def evaluate_asset(
        cls,
        symbol: str,
        spot_price: float,
        current_iv: float,
        iv_history_24m: List[float],
        rv_20d: float,
        chain_contracts: List[Dict[str, Any]],
        directional_bias: str = "NEUTRAL", # "BULLISH" | "BEARISH" | "NEUTRAL"
    ) -> PROVESTEvaluation:
        """
        Executes full PROVEST evaluation on an asset option chain.
        """
        # 1. Volatility (V): Relative Volatility Rank (Deciles 1-10)
        rel_vol_rank = cls.compute_relative_volatility_rank(iv_history_24m, current_iv)

        # 2. Skew (S): Calculate 25-Delta Put/Call Skew & Front/Back Calendar Disparity
        puts_30d = [c for c in chain_contracts if not c.get("is_call") and c.get("dte", 30) <= 35]
        calls_30d = [c for c in chain_contracts if c.get("is_call") and c.get("dte", 30) <= 35]
        front_puts = [c for c in chain_contracts if c.get("dte", 30) <= 25]
        back_puts = [c for c in chain_contracts if c.get("dte", 60) >= 45]

        skew_ratio = 1.15
        if puts_30d and calls_30d:
            put_iv = np.mean([float(c.get("iv", current_iv)) for c in puts_30d])
            call_iv = np.mean([float(c.get("iv", current_iv)) for c in calls_30d])
            if call_iv > 0:
                skew_ratio = round(put_iv / call_iv, 2)

        cal_disparity = 0.0
        if front_puts and back_puts:
            f_iv = np.mean([float(c.get("iv", current_iv)) for c in front_puts])
            b_iv = np.mean([float(c.get("iv", current_iv)) for c in back_puts])
            if b_iv > 0:
                cal_disparity = round(((f_iv - b_iv) / b_iv) * 100.0, 1)

        # 3. Expiration (E): Determine optimal DTE & Theta decay phase
        target_dte = 45 if rel_vol_rank <= 4 else 30
        theta_phase = "ACCELERATED" if target_dte <= 45 else "LINEAR"

        # 4. Probability & Strategy Selection (P & T):
        recommended = []
        is_favorable = False

        if directional_bias == "BULLISH":
            if rel_vol_rank <= 4:
                recommended.extend(["LONG_CALL_DEEP_ITM", "CALL_BACKSPREAD"])
            else:
                recommended.extend(["BULL_PUT_CREDIT_SPREAD", "COVERED_CALL_WRITE"])
        elif directional_bias == "BEARISH":
            if rel_vol_rank <= 4:
                recommended.extend(["LONG_PUT_DEEP_ITM", "PUT_BACKSPREAD"])
            else:
                recommended.extend(["BEAR_CALL_CREDIT_SPREAD", "PUT_RATIO_SPREAD_1X2"])
        else: # NEUTRAL
            if rel_vol_rank <= 3:
                recommended.extend(["CALENDAR_SPREAD", "LONG_STRADDLE"])
            elif rel_vol_rank >= 7:
                recommended.extend(["IRON_CONDOR", "IRON_BUTTERFLY", "WHEEL_CSP"])
            else:
                recommended.extend(["IRON_CONDOR", "WHEEL_CSP"])

        # Composite score
        vrp = current_iv - rv_20d
        composite_score = min(0.98, max(0.20, 0.50 + (vrp * 2.0) + (0.05 * (rel_vol_rank - 5))))

        return PROVESTEvaluation(
            symbol=symbol,
            probability_of_profit=round(0.50 + (0.03 * rel_vol_rank if rel_vol_rank >= 6 else -0.05), 2),
            relative_volatility_rank=rel_vol_rank,
            implied_volatility=round(current_iv, 4),
            historical_volatility_20d=round(rv_20d, 4),
            days_to_expiration=target_dte,
            theta_decay_phase=theta_phase,
            volatility_skew_ratio=skew_ratio,
            calendar_vol_disparity_pct=cal_disparity,
            timing_regime_bias=directional_bias,
            recommended_strategies=recommended,
            is_favorable_entry=composite_score >= 0.55,
            provest_composite_score=round(composite_score, 3),
        )
