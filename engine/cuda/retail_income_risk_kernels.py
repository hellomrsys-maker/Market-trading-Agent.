"""
Module AR6 (CUDA): Mass GPU Parallel Retail Income Risk Governor Kernels.
Vectorized batch auditing of 5% single-underlying caps, 25% cash buffer compliance, and 14-day earnings filters.
"""

import numpy as np


def batch_audit_retail_income_risk_cuda(
    equity_arr: np.ndarray,
    free_cash_arr: np.ndarray,
    proposed_collateral_arr: np.ndarray,
    existing_collateral_arr: np.ndarray,
    days_earnings_arr: np.ndarray
) -> np.ndarray:
    """
    Vectorized CUDA GPU kernel simulator:
    Computes cash buffer %, symbol cap flags, cash buffer flags, earnings safety flags, and trade approval flags.
    """
    max_allocations = equity_arr * 0.05
    total_exposures = existing_collateral_arr + proposed_collateral_arr
    symbol_cap_ok = np.where(total_exposures <= max_allocations, 1.0, 0.0)

    remaining_cash = free_cash_arr - proposed_collateral_arr
    cash_buffer_pcts = (remaining_cash / np.maximum(1.0, equity_arr)) * 100.0
    cash_buffer_ok = np.where(cash_buffer_pcts >= 25.0, 1.0, 0.0)

    earnings_safe = np.where(days_earnings_arr >= 14, 1.0, 0.0)
    approved = np.where((symbol_cap_ok == 1.0) & (cash_buffer_ok == 1.0) & (earnings_safe == 1.0), 1.0, 0.0)

    # Return shape (N, 5): [cash_buffer_pct, symbol_cap_ok, cash_buffer_ok, earnings_safe, approved]
    return np.column_stack([cash_buffer_pcts, symbol_cap_ok, cash_buffer_ok, earnings_safe, approved])
