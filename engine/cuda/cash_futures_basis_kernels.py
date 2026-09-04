"""
Module AV6 (CUDA): Mass GPU Parallel Cash-to-Futures Basis Kernels.
Vectorized batch calculation of local cash basis Z-scores and cash-and-carry storage arbitrage profits.
"""

import numpy as np


def batch_compute_cash_futures_basis_cuda(
    cash_prices: np.ndarray,
    futures_prices: np.ndarray,
    basis_means: np.ndarray,
    basis_stds: np.ndarray,
    carrying_costs: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes basis, basis Z-scores, regime flags (1 Strong, -1 Weak, 0 Normal), and net arbitrage profits.
    """
    bases = cash_prices - futures_prices
    stds = np.maximum(1e-4, basis_stds)
    zscores = (bases - basis_means) / stds

    regimes = np.where(zscores >= 1.5, 1.0, np.where(zscores <= -1.5, -1.0, 0.0))
    net_profits = (futures_prices - cash_prices) - carrying_costs
    profitable_carry = np.where(net_profits > 0.0, 1.0, 0.0)

    # Return shape (N, 5): [basis, zscore, regime, net_profit, profitable_carry]
    return np.column_stack([bases, zscores, regimes, net_profits, profitable_carry])
