"""
CUDA GPU Parallel Kernels for Structured Collar & Box Arbitrage (Module BH6 - Python/CUDA)
Processes 100,000 algorithmic structured options evaluations simultaneously.
"""

from numba import cuda
import numpy as np

@cuda.jit
def structured_collar_box_kernel(basis, call_k, call_prem, put_k, put_prem, box_k1, box_k2, box_debit, bet, payout_pct, itm, results):
    i = cuda.grid(1)
    if i < basis.size:
        net_collar = call_prem[i] - put_prem[i]
        box_profit = (box_k2[i] - box_k1[i]) - box_debit[i]
        bin_payout = bet[i] * (payout_pct[i] / 100.0) if itm[i] == 1.0 else -bet[i] * 0.90
        
        results[i, 0] = net_collar
        results[i, 1] = 1.0 if net_collar >= 0.0 else 0.0
        results[i, 2] = box_profit
        results[i, 3] = 1.0 if box_profit > 0.0 else 0.0
        results[i, 4] = bin_payout
