"""
Module AG6 (CUDA): Mass GPU Parallel VIX Term Structure & Roll Yield Kernels.
Vectorized batch calculation of term slope, annualized roll yields, and VVIX surge flags.
"""

import numpy as np


def batch_compute_vix_term_structure_cuda(
    m1_arr: np.ndarray,
    m2_arr: np.ndarray,
    delta_days_arr: np.ndarray,
    vvix_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes slope, annualized roll yield %, contango flags, and tail risk flags.
    """
    slopes = m2_arr - m1_arr
    delta_days = np.maximum(1, delta_days_arr)
    roll_yields = ((m2_arr - m1_arr) / np.maximum(1e-5, m1_arr)) * (365.0 / delta_days) * 100.0
    contango_flags = np.where(slopes > 0.15, 1.0, np.where(slopes < -0.15, -1.0, 0.0))
    tail_risk_flags = np.where(vvix_arr >= 115.0, 1.0, 0.0)

    # Return shape (N, 4): [slope, roll_yield, contango_flag, tail_risk_flag]
    return np.column_stack([slopes, roll_yields, contango_flags, tail_risk_flags])
