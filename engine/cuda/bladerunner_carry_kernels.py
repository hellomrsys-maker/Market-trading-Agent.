"""
CUDA GPU Parallel Kernels for Bladerunner Forex & Carry Trade (Module BG6 - Python/CUDA)
Processes 100,000 algorithmic Forex evaluations simultaneously.
"""

from numba import cuda
import numpy as np

@cuda.jit
def bladerunner_carry_kernel(spot, ema20, rejected, confirmed, rate_long, rate_short, units, win_prob, win_loss, results):
    i = cuda.grid(1)
    if i < spot.size:
        above = 1.0 if spot[i] > ema20[i] else 0.0
        
        action = 0.0
        if above == 1.0 and rejected[i] == 1.0 and confirmed[i] == 1.0:
            action = 1.0
        elif above == 0.0 and rejected[i] == 1.0 and confirmed[i] == 1.0:
            action = 2.0
            
        diff = (rate_long[i] - rate_short[i]) / 100.0
        daily_int = (diff * units[i]) / 365.0
        
        w = max(0.01, min(0.99, win_prob[i]))
        r = max(0.01, win_loss[i])
        k = w - ((1.0 - w) / r)
        alloc = max(0.0, min(0.25, k))
        
        results[i, 0] = action
        results[i, 1] = daily_int
        results[i, 2] = alloc
