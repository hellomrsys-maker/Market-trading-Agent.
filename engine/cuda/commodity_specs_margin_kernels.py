"""
Module AS6 (CUDA): Mass GPU Parallel Commodity Specs & SPAN Margin Kernels.
Vectorized batch calculation of SPAN margin excess, utilization %, and liquidation proximity scores.
"""

import numpy as np


def batch_compute_margin_health_cuda(
    equity_arr: np.ndarray,
    initial_margin_arr: np.ndarray,
    maint_margin_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes margin excess, utilization %, proximity scores, safe flags, and margin call flags.
    """
    excess = equity_arr - maint_margin_arr
    utilization = (initial_margin_arr / np.maximum(1.0, equity_arr)) * 100.0

    denominator = np.maximum(1.0, initial_margin_arr - maint_margin_arr)
    proximity = (equity_arr - maint_margin_arr) / denominator
    safe_flags = np.where(proximity >= 1.0, 1.0, 0.0)
    call_flags = np.where(equity_arr < maint_margin_arr, 1.0, 0.0)

    # Return shape (N, 5): [excess, utilization, proximity, safe_flag, call_flag]
    return np.column_stack([excess, utilization, proximity, safe_flags, call_flags])
