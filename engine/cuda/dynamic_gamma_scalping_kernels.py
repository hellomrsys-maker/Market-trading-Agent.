"""
Module AH6 (CUDA): Mass GPU Parallel Dynamic Gamma Scalping Kernels.
Vectorized batch calculation of Leland-Whalley-Wilmott rebalancing bands and discrete scalping PnL.
"""

import numpy as np


def batch_compute_gamma_scalp_cuda(
    gamma_arr: np.ndarray,
    spot_arr: np.ndarray,
    current_delta_arr: np.ndarray,
    realized_vol_arr: np.ndarray,
    implied_vol_arr: np.ndarray,
    tx_cost: float = 0.005,
    risk_aversion: float = 1.0
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes optimal delta thresholds, rebalance signals, and scalping PnLs.
    """
    abs_gamma = np.maximum(1e-7, np.abs(gamma_arr))
    term = (1.5 * tx_cost * abs_gamma) / max(1e-5, risk_aversion)
    thresholds = np.clip(np.cbrt(term), 0.02, 0.25)

    delta_drifts = np.abs(current_delta_arr)
    triggers = np.where(delta_drifts >= thresholds, 1.0, 0.0)
    rebalance_shares = np.where(triggers == 1.0, -current_delta_arr * 100.0, 0.0)

    gamma_dollar = 0.5 * gamma_arr * (spot_arr ** 2)
    var_diffs = (realized_vol_arr ** 2) - (implied_vol_arr ** 2)
    daily_gross_pnl = gamma_dollar * var_diffs * (1.0 / 252.0)

    # Return shape (N, 4): [threshold, trigger_flag, rebalance_shares, daily_gross_pnl]
    return np.column_stack([thresholds, triggers, rebalance_shares, daily_gross_pnl])
