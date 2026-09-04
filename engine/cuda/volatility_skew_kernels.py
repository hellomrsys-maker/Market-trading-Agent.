"""
Module AY6 (CUDA): Mass GPU Parallel Volatility Skew & BWB Kernels.
Vectorized batch calculation of strike skew slopes, term structure slopes, and Broken Wing Butterfly economics.
"""

import numpy as np


def batch_compute_volatility_skew_cuda(
    iv_atm_arr: np.ndarray,
    iv_put25_arr: np.ndarray,
    iv_call25_arr: np.ndarray,
    iv_30_arr: np.ndarray,
    iv_90_arr: np.ndarray,
    c1_arr: np.ndarray,
    c2_arr: np.ndarray,
    c3_arr: np.ndarray,
    k1_arr: np.ndarray,
    k2_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes strike skew slopes, term structure slopes, BWB net credits, and zero downside risk flags.
    """
    strike_skews = (iv_put25_arr - iv_call25_arr) / np.maximum(1e-4, iv_atm_arr)
    term_slopes = (iv_90_arr - iv_30_arr) / np.maximum(1e-4, iv_30_arr)

    steep_puts = np.where(strike_skews >= 0.25, 1.0, 0.0)
    net_credits = (2.0 * c2_arr) - c1_arr - c3_arr
    max_profits = (k2_arr - k1_arr) + net_credits
    zero_risks = np.where(net_credits >= 0.0, 1.0, 0.0)

    # Return shape (N, 5): [strike_skew, term_slope, steep_put, net_credit, zero_risk]
    return np.column_stack([strike_skews, term_slopes, steep_puts, net_credits, zero_risks])
