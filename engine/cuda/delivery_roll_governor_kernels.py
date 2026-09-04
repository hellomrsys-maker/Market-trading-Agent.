"""
Module AT6 (CUDA): Mass GPU Parallel Delivery Risk & Roll Governor Kernels.
Vectorized batch calculation of volume crossovers, FND danger alerts, and roll execution directives.
"""

import numpy as np


def batch_compute_delivery_rolls_cuda(
    is_physical_arr: np.ndarray,
    days_fnd_arr: np.ndarray,
    vol_m1_arr: np.ndarray,
    vol_m2_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes volume crossover flags, FND danger flags, and action directives (0 Hold, 1 Roll, 2 Liquidate).
    """
    vol_cross = np.where(vol_m2_arr > vol_m1_arr, 1.0, 0.0)
    fnd_danger = np.where((is_physical_arr == 1.0) & (days_fnd_arr <= 5), 1.0, 0.0)

    actions = np.zeros_like(is_physical_arr)
    actions = np.where((is_physical_arr == 1.0) & (days_fnd_arr <= 1), 2.0, actions)
    actions = np.where((actions == 0.0) & ((fnd_danger == 1.0) | (vol_cross == 1.0)), 1.0, actions)

    # Return shape (N, 3): [vol_cross, fnd_danger, action_directive]
    return np.column_stack([vol_cross, fnd_danger, actions])
