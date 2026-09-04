"""
Module AP6 (CUDA): Mass GPU Parallel Covered Call Yield Kernels.
Vectorized batch calculation of annualized static yield, max upside yield, and ex-dividend assignment risk flags.
"""

import numpy as np


def batch_compute_covered_call_yield_cuda(
    stock_basis_arr: np.ndarray,
    current_spot_arr: np.ndarray,
    strike_arr: np.ndarray,
    call_prem_arr: np.ndarray,
    dte_arr: np.ndarray,
    dividend_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes annualized static yield %, max yield %, and early assignment flags.
    """
    static_yield = ((call_prem_arr + dividend_arr) / np.maximum(1e-5, stock_basis_arr)) * 100.0
    ann_static = static_yield * (365.0 / np.maximum(1.0, dte_arr))

    cap_gains = np.maximum(0.0, strike_arr - stock_basis_arr)
    max_yield = ((cap_gains + call_prem_arr + dividend_arr) / np.maximum(1e-5, stock_basis_arr)) * 100.0
    ann_max = max_yield * (365.0 / np.maximum(1.0, dte_arr))

    intrinsics = np.maximum(0.0, current_spot_arr - strike_arr)
    extrinsics = np.maximum(0.0, call_prem_arr - intrinsics)
    early_assignment = np.where((current_spot_arr > strike_arr) & (extrinsics < dividend_arr), 1.0, 0.0)

    # Return shape (N, 4): [ann_static, ann_max, extrinsics, early_assignment]
    return np.column_stack([ann_static, ann_max, extrinsics, early_assignment])
