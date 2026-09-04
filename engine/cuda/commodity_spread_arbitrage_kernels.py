"""
Module AL6 (CUDA): Mass GPU Parallel Commodity Processing & Spreads Kernels.
Vectorized batch calculation of 3:2:1 energy cracks, soybean crush GPM, and cost-of-carry.
"""

import numpy as np


def batch_compute_commodity_spreads_cuda(
    cl_arr: np.ndarray,
    rbob_arr: np.ndarray,
    ho_arr: np.ndarray,
    beans_arr: np.ndarray,
    meal_arr: np.ndarray,
    oil_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes crack margins ($/bbl), crush GPM (cents/bu), crack signals, and crush signals.
    """
    gas_bbl = rbob_arr * 42.0
    ho_bbl = ho_arr * 42.0
    crack_margins = ((2.0 * gas_bbl + ho_bbl) - (3.0 * cl_arr)) / 3.0
    crack_signals = np.where(crack_margins >= 25.0, -1.0, np.where(crack_margins <= 10.0, 1.0, 0.0))

    meal_rev = meal_arr * 2.2
    oil_rev = oil_arr * 11.0
    crush_gpm = (meal_rev + oil_rev) - beans_arr
    crush_signals = np.where(crush_gpm > 180.0, -1.0, np.where(crush_gpm < 60.0, 1.0, 0.0))

    # Return shape (N, 4): [crack_margin, crack_signal, crush_gpm, crush_signal]
    return np.column_stack([crack_margins, crack_signals, crush_gpm, crush_signals])
