"""
Module AZ6 (CUDA): Mass GPU Parallel Trade Adjustment & Repair Kernels.
Vectorized batch calculation of trade defense triggers, delta breaches, and repair action directives.
"""

import numpy as np


def batch_compute_trade_defense_cuda(
    pnl_arr: np.ndarray,
    credit_arr: np.ndarray,
    short_delta_arr: np.ndarray,
    dte_arr: np.ndarray,
    extrinsic_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes delta breach flags, max loss hit flags, and action directives (0 Hold, 1 Cut, 2 Wing Roll, 3 Time Roll, 4 Delta Hedge).
    """
    delta_breached = np.where(np.abs(short_delta_arr) >= 0.35, 1.0, 0.0)
    max_loss_hit = np.where(pnl_arr <= -(credit_arr * 2.0), 1.0, 0.0)

    actions = np.zeros_like(pnl_arr)
    actions = np.where(max_loss_hit == 1.0, 1.0, actions)
    actions = np.where((actions == 0.0) & (delta_breached == 1.0) & (dte_arr >= 14.0) & (extrinsic_arr > 0.30), 2.0, actions)
    actions = np.where((actions == 0.0) & (delta_breached == 1.0) & (dte_arr < 7.0), 3.0, actions)
    actions = np.where((actions == 0.0) & (delta_breached == 1.0), 4.0, actions)

    # Return shape (N, 3): [delta_breached, max_loss_hit, action_directive]
    return np.column_stack([delta_breached, max_loss_hit, actions])
