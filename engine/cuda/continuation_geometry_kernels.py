"""
Module BB6 (CUDA): Mass GPU Parallel Continuation Geometry Pattern Kernels.
Vectorized batch calculation of triangle compressions, flags, pennants, and continuation price projections.
"""

import numpy as np


def batch_compute_continuation_geometry_cuda(
    breakout_px_arr: np.ndarray,
    dim_height_arr: np.ndarray,
    spot_arr: np.ndarray,
    is_bullish_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes measured continuation targets and confirmed breakout flags.
    """
    targets = np.where(is_bullish_arr == 1.0, breakout_px_arr + dim_height_arr, breakout_px_arr - dim_height_arr)
    breakouts = np.where(
        (is_bullish_arr == 1.0) & (spot_arr > breakout_px_arr), 1.0,
        np.where((is_bullish_arr == 0.0) & (spot_arr < breakout_px_arr), 1.0, 0.0)
    )

    # Return shape (N, 2): [measured_target, is_breakout]
    return np.column_stack([targets, breakouts])
