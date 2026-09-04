"""
engine/cuda/cliquet_mountain_kernels.py
=======================================
OptionAlpha Agent — Module W6: CUDA GPU Kernels for Cliquet & Mountain Range Structures
"""

import torch

def gpu_batch_gflc_cliquets(
    returns_matrix: torch.Tensor, # Shape: (batch_size, n_periods)
    local_floor: float,
    local_cap: float,
    global_floor: float,
    global_cap: float
) -> torch.Tensor:
    """
    Mass GPU batch computation of Globally Floored Locally Capped Cliquets:
    Payoff = clamp(sum(clamp(returns, min=LF, max=LC)), min=GF, max=GC)
    """
    clipped = torch.clamp(returns_matrix, min=local_floor, max=local_cap)
    sums = torch.sum(clipped, dim=-1)
    gflc = torch.clamp(sums, min=global_floor, max=global_cap)
    return gflc
