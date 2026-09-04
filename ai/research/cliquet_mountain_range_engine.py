"""
ai/research/cliquet_mountain_range_engine.py
============================================
OptionAlpha Agent — Module W1: Python Cliquet, Napoleon & Mountain Range Pricing Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Tuple

class CliquetMountainRangeEngine:
    """
    Synthesizes 'Exotic Options and Hybrids' (Bouzoubaa & Osseiran) - Part III Chapters 13, 14, 15:
    - The Cliquet Family: LFLC, GFLC, Reverse Cliquets
    - Accumulators / Lock-in Cliquets & Napoleons
    - Lookback Options (Max/Min Spot Goldman-Sosin-Gatto 1979)
    - Mountain Range Suite: Altiplano, Himalaya, Everest, Kilimanjaro Select, Atlas
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    @staticmethod
    def calculate_lflc_cliquet(
        periodic_returns: List[float],
        local_floor: float,
        local_cap: float
    ) -> float:
        """
        Locally Floored Locally Capped Cliquet Payoff:
        Payoff = sum_{i=1}^n max[LocalFloor, min(Ret_i, LocalCap)]
        """
        payoff = sum(max(local_floor, min(r, local_cap)) for r in periodic_returns)
        return float(payoff)

    @staticmethod
    def calculate_gflc_cliquet(
        periodic_returns: List[float],
        local_floor: float,
        local_cap: float,
        global_floor: float,
        global_cap: float
    ) -> float:
        """
        Globally Floored Locally Capped (GFLC) Cliquet:
        Payoff = max[GlobalFloor, min(GlobalCap, sum(max(LocalFloor, min(Ret_i, LocalCap))))]
        """
        raw_sum = sum(max(local_floor, min(r, local_cap)) for r in periodic_returns)
        payoff = max(global_floor, min(global_cap, raw_sum))
        return float(payoff)

    @staticmethod
    def calculate_napoleon_payoff(
        periodic_returns: List[float],
        max_coupon: float
    ) -> float:
        """
        Napoleon Structure Payoff:
        Payoff = max[0, MaxCoupon + min(Ret_i)]
        """
        worst_return = min(periodic_returns) if periodic_returns else 0.0
        return max(0.0, float(max_coupon + worst_return))

    @staticmethod
    def calculate_himalaya_payoff(
        asset_trajectories: np.ndarray, # Shape: (n_periods, n_assets)
        participation: float = 1.0,
        strike: float = 1.0
    ) -> float:
        """
        Himalaya Option:
        At each observation date t_i, the best performing asset in the basket is removed
        and its performance is frozen into the running average.
        """
        n_periods, n_assets = asset_trajectories.shape
        active_indices = list(range(n_assets))
        frozen_performances = []

        for t in range(n_periods):
            if not active_indices:
                break
            best_idx = max(active_indices, key=lambda idx: asset_trajectories[t, idx])
            frozen_performances.append(asset_trajectories[t, best_idx])
            active_indices.remove(best_idx)

        avg_perf = float(np.mean(frozen_performances))
        payoff = participation * max(0.0, avg_perf - strike)
        return payoff

    @staticmethod
    def calculate_everest_payoff(
        final_returns: List[float],
        coupon: float = 2.0
    ) -> float:
        """
        Everest Option:
        100% capital guaranteed + bonus linked to the worst-performing stock in a basket (N >= 10):
        Payoff = Coupon + min(Ret_j(T))
        """
        worst_perf = min(final_returns) if final_returns else 0.0
        return float(coupon + worst_perf)
