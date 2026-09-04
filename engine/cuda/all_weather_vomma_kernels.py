"""
CUDA GPU Parallel Kernels for All-Weather Vomma (Module BE6 - Python/CUDA)
Processes 100,000 SPAN margin slice scenarios simultaneously.
"""

from numba import cuda
import numpy as np
import math

@cuda.jit
def all_weather_vomma_kernel(pnl_12_down, pnl_20_down, pnl_10_up, capital, vix_spike, results):
    i = cuda.grid(1)
    if i < pnl_12_down.size:
        s12 = abs(min(0.0, pnl_12_down[i]))
        s20 = abs(min(0.0, pnl_20_down[i])) / 2.0
        s10 = abs(min(0.0, pnl_10_up[i]))
        
        req = max(s12, max(s20, s10))
        util = (req / max(1.0, capital[i])) * 100.0
        
        results[i, 0] = req
        results[i, 1] = util
        results[i, 2] = 1.0 if util <= 65.0 else 0.0
        results[i, 3] = 4.0 if vix_spike[i] >= 35.0 else 1.0
