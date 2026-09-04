"""
Module AO6 (CUDA): Mass GPU Parallel Cash-Secured Put (CSP) Kernels.
Vectorized batch calculation of effective acquisition bases, annualized ROC %, and POP statistics.
"""

import numpy as np


def batch_compute_csp_opportunities_cuda(
    spot_arr: np.ndarray,
    strike_arr: np.ndarray,
    premium_arr: np.ndarray,
    dte_arr: np.ndarray,
    delta_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes effective bases, discounts %, annualized ROC %, and optimal setup flags.
    """
    effective_bases = strike_arr - premium_arr
    discounts_pct = ((spot_arr - effective_bases) / np.maximum(1e-5, spot_arr)) * 100.0
    
    collateral = strike_arr * 100.0
    trade_roc = (premium_arr * 100.0 / np.maximum(1e-5, collateral)) * 100.0
    annualized_roc = trade_roc * (365.0 / np.maximum(1.0, dte_arr))

    abs_deltas = np.abs(delta_arr)
    pop_pcts = (1.0 - abs_deltas) * 100.0
    is_optimal = np.where(
        (abs_deltas >= 0.20) & (abs_deltas <= 0.30) & (dte_arr >= 30.0) & (dte_arr <= 45.0),
        1.0, 0.0
    )

    # Return shape (N, 5): [effective_basis, discount_pct, annualized_roc, pop_pct, is_optimal]
    return np.column_stack([effective_bases, discounts_pct, annualized_roc, pop_pcts, is_optimal])
