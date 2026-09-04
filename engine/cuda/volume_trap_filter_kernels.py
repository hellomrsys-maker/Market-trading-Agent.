"""
Module BC6 (CUDA): Mass GPU Parallel Volume Breakout & Trap Filter Kernels.
Vectorized batch calculation of volume surge ratios and Wyckoff Spring/Upthrust trap detections.
"""

import numpy as np


def batch_compute_volume_traps_cuda(
    vol_arr: np.ndarray,
    sma_vol_arr: np.ndarray,
    key_level_arr: np.ndarray,
    extreme_px_arr: np.ndarray,
    close_px_arr: np.ndarray,
    is_support_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes volume surge ratios, volume confirmation flags, and trap detection flags.
    """
    surge_ratios = vol_arr / np.maximum(1.0, sma_vol_arr)
    vol_confirmed = np.where(surge_ratios >= 1.50, 1.0, 0.0)

    springs = np.where((is_support_arr == 1.0) & (extreme_px_arr < key_level_arr) & (close_px_arr >= key_level_arr), 1.0, 0.0)
    upthrusts = np.where((is_support_arr == 0.0) & (extreme_px_arr > key_level_arr) & (close_px_arr <= key_level_arr), 1.0, 0.0)
    traps = np.where((springs == 1.0) | (upthrusts == 1.0), 1.0, 0.0)

    # Return shape (N, 3): [surge_ratio, vol_confirmed, is_trap]
    return np.column_stack([surge_ratios, vol_confirmed, traps])
