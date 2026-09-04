"""
Module AJ6 (CUDA): Mass GPU Parallel Statistical Mean Reversion Kernels.
Vectorized batch calculation of rolling Z-scores, entry/exit thresholds, and stop triggers.
"""

import numpy as np


def batch_compute_zscore_signals_cuda(
    values_arr: np.ndarray,
    rolling_means_arr: np.ndarray,
    rolling_stds_arr: np.ndarray,
    hurst_arr: np.ndarray,
    z_entry: float = 2.0,
    z_exit: float = 0.5,
    z_stop: float = 3.5
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes Z-scores, trade signal actions (+1 Long, -1 Short, 0 Exit, 99 Stop), and regime flags.
    """
    stds = np.maximum(1e-5, rolling_stds_arr)
    zscores = (values_arr - rolling_means_arr) / stds

    actions = np.zeros_like(zscores)
    # Stop condition
    actions = np.where(np.abs(zscores) >= z_stop, 99.0, actions)
    # Entry conditions
    actions = np.where((actions == 0.0) & (zscores >= z_entry), -1.0, actions)
    actions = np.where((actions == 0.0) & (zscores <= -z_entry), 1.0, actions)
    # Exit condition
    actions = np.where((actions == 0.0) & (np.abs(zscores) <= z_exit), 0.0, actions)

    mean_reverting_flags = np.where(hurst_arr < 0.45, 1.0, 0.0)

    # Return shape (N, 3): [zscore, signal_action, is_mean_reverting]
    return np.column_stack([zscores, actions, mean_reverting_flags])
