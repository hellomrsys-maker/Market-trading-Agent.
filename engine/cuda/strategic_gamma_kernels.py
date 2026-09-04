"""
Module AF6 (CUDA): Mass GPU Parallel Strategic Gamma Scalping & Rent Breakeven Kernels.
Vectorized batch evaluation of Gamma Decay Breakeven (Delta_S = sqrt(2*Theta/Gamma)) and daily sigma moves.
"""

import numpy as np

def batch_gamma_decay_breakeven_cuda(
    theta_arr: np.ndarray,
    gamma_arr: np.ndarray
) -> np.ndarray:
    """
    Simulated GPU kernel for calculating 'The Rent' Gamma Decay Breakeven:
    Delta_S = sqrt(2 * Theta / Gamma)
    """
    safe_gamma = np.maximum(gamma_arr, 1e-6)
    abs_theta = np.abs(theta_arr)
    decay_moves = np.sqrt((2.0 * abs_theta) / safe_gamma)
    return decay_moves

def batch_daily_sigma_moves_cuda(
    spots: np.ndarray,
    annual_vols: np.ndarray
) -> np.ndarray:
    """
    Simulated GPU kernel for daily standard deviation moves.
    """
    daily_vols = annual_vols / np.sqrt(252.0)
    sigma1 = spots * daily_vols
    sigma2 = sigma1 * 2.0
    return np.column_stack((daily_vols, sigma1, sigma2))
