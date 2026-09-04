"""
Module AQ6 (CUDA): Mass GPU Parallel Wheel Strategy Lifecycle Kernels.
Vectorized batch calculation of true amortized net cost bases and 50% profit target flags.
"""

import numpy as np


def batch_compute_wheel_lifecycle_cuda(
    state_arr: np.ndarray,
    spot_arr: np.ndarray,
    cost_basis_arr: np.ndarray,
    accum_income_arr: np.ndarray,
    strike_arr: np.ndarray,
    orig_prem_arr: np.ndarray,
    curr_prem_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes true net cost basis, profit captured %, and 50% profit target flags.
    """
    true_net_bases = cost_basis_arr - accum_income_arr
    profit_captured = orig_prem_arr - curr_prem_arr
    profit_pcts = np.where(orig_prem_arr > 0, (profit_captured / np.maximum(1e-5, orig_prem_arr)) * 100.0, 0.0)
    hit_50 = np.where(profit_pcts >= 50.0, 1.0, 0.0)

    # Return shape (N, 3): [true_net_basis, profit_pct, hit_50]
    return np.column_stack([true_net_bases, profit_pcts, hit_50])
