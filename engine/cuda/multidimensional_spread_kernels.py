"""
Module AE6 (CUDA): Mass GPU Parallel Multi-Dimensional Spread & Wing Kernels.
Vectorized batch evaluation of 1x2 Ratio Spreads, 2x1 Backspreads, and Butterflies.
"""

import numpy as np

def batch_ratio_spread_cuda(
    k1_arr: np.ndarray,
    k2_arr: np.ndarray,
    prem_long_arr: np.ndarray,
    prem_short_arr: np.ndarray
) -> np.ndarray:
    """
    Simulated GPU kernel for batch 1x2 Call/Put ratio spreads.
    """
    net_cashes = (2.0 * prem_short_arr) - prem_long_arr
    strike_diffs = k2_arr - k1_arr
    max_profits = strike_diffs + net_cashes
    upside_bes = k2_arr + max_profits
    escape_strikes = k2_arr + strike_diffs

    return np.column_stack((net_cashes, max_profits, upside_bes, escape_strikes))

def batch_backspread_cuda(
    k1_arr: np.ndarray,
    k2_arr: np.ndarray,
    prem_short_arr: np.ndarray,
    prem_long_arr: np.ndarray
) -> np.ndarray:
    """
    Simulated GPU kernel for batch 2x1 Backspreads.
    """
    net_credits = prem_short_arr - (2.0 * prem_long_arr)
    strike_diffs = k2_arr - k1_arr
    max_losses = np.maximum(0.0, strike_diffs - net_credits)
    upside_bes = k2_arr + strike_diffs - net_credits

    return np.column_stack((net_credits, max_losses, upside_bes))
