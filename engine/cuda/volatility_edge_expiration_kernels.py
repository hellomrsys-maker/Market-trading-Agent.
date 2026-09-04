"""
Module AI6 (CUDA): Mass GPU Parallel Volatility Edge & Expiration Kernels.
Vectorized batch calculation of strike pinning gravity, Vega/Theta risk ratios, and touch probabilities.
"""

import numpy as np


def batch_compute_expiration_edge_cuda(
    spot_arr: np.ndarray,
    strike_arr: np.ndarray,
    dte_arr: np.ndarray,
    oi_arr: np.ndarray,
    vega_arr: np.ndarray,
    theta_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes pinning gravitational pull, candidate flags, and vega/theta risk ratios.
    """
    distances = np.abs(spot_arr - strike_arr)
    t_factors = np.exp(-np.maximum(0.01, dte_arr) * 2.0)
    pull_scores = (oi_arr / ((distances ** 2) + 1.0)) * t_factors

    is_pinning = np.where((distances < 2.0) & (dte_arr <= 1.0) & (oi_arr > 5000), 1.0, 0.0)

    abs_thetas = np.maximum(1e-4, np.abs(theta_arr))
    vt_ratios = np.abs(vega_arr) / abs_thetas
    balanced_flags = np.where(vt_ratios <= 3.5, 1.0, 0.0)

    # Return shape (N, 4): [pull_score, is_pinning_flag, vt_ratio, balanced_flag]
    return np.column_stack([pull_scores, is_pinning, vt_ratios, balanced_flags])
