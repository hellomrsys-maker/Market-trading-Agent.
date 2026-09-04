"""
Module AC6 (CUDA): Mass GPU Parallel Options Equivalency & Arbitrage Kernels.
Vectorized batch evaluation of Put-Call parity and Box Spread arbitrage.
"""

import numpy as np

def batch_evaluate_put_call_parity_cuda(
    stock_prices: np.ndarray,
    strike_prices: np.ndarray,
    call_mids: np.ndarray,
    put_mids: np.ndarray,
    bases: np.ndarray
) -> np.ndarray:
    """
    Simulated GPU kernel for batch Put-Call parity theoretical stock price & arbitrage discrepancy.
    """
    theo_stocks = call_mids - put_mids + strike_prices - bases
    discrepancies = stock_prices - theo_stocks
    is_arb = (np.abs(discrepancies) > 0.05).astype(np.int32)
    return np.column_stack((theo_stocks, discrepancies, is_arb))

def batch_evaluate_box_spreads_cuda(
    call_spreads: np.ndarray,
    put_spreads: np.ndarray,
    k1_strikes: np.ndarray,
    k2_strikes: np.ndarray
) -> np.ndarray:
    """
    Simulated GPU kernel for batch Box Spread guaranteed profits.
    """
    box_costs = call_spreads + put_spreads
    par_values = np.abs(k2_strikes - k1_strikes)
    profits = par_values - box_costs
    is_arb = (profits > 0.05).astype(np.int32)
    return np.column_stack((box_costs, profits, is_arb))
