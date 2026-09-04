"""
Module AK6 (CUDA): Mass GPU Parallel Schwager Price Action & Trap Kernels.
Vectorized batch calculation of key reversal days, spring/upthrust traps, and gap extensions.
"""

import numpy as np


def batch_compute_schwager_price_action_cuda(
    prev_lows: np.ndarray,
    prev_highs: np.ndarray,
    prev_closes: np.ndarray,
    curr_lows: np.ndarray,
    curr_highs: np.ndarray,
    curr_closes: np.ndarray,
    curr_volumes: np.ndarray,
    avg_volumes: np.ndarray,
    supports: np.ndarray,
    resistances: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes key reversal flags (+1 Bull, -1 Bear, 0 None), trap flags (+1 Spring, -1 Upthrust, 0 None), and stop levels.
    """
    vol_surge = np.where(avg_volumes <= 0, True, curr_volumes >= avg_volumes * 1.3)

    is_bull_rev = (curr_lows < prev_lows) & (curr_closes > prev_closes) & vol_surge
    is_bear_rev = (curr_highs > prev_highs) & (curr_closes < prev_closes) & vol_surge

    key_flags = np.where(is_bull_rev, 1.0, np.where(is_bear_rev, -1.0, 0.0))

    is_spring = (curr_lows < supports) & (curr_closes >= supports)
    is_upthrust = (curr_highs > resistances) & (curr_closes <= resistances)
    trap_flags = np.where(is_spring, 1.0, np.where(is_upthrust, -1.0, 0.0))

    stop_levels = np.where(is_bull_rev, curr_lows, np.where(is_bear_rev, curr_highs, 0.0))

    # Return shape (N, 3): [key_reversal_flag, trap_flag, stop_level]
    return np.column_stack([key_flags, trap_flags, stop_levels])
