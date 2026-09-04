"""
engine/cuda/barrier_autocallable_kernels.py
===========================================
OptionAlpha Agent — Module V6: CUDA GPU Kernels for Discrete Barrier Shifts & Digitals
"""

import torch

def gpu_batch_discrete_barrier_shifts(
    barriers: torch.Tensor,
    sigmas: torch.Tensor,
    t_years: torch.Tensor,
    num_observations: torch.Tensor,
    is_short: bool = True
) -> torch.Tensor:
    """
    Broadie-Glasserman-Kou discrete monitoring shift across 10,000+ contracts:
    H' = H * exp(+/- 0.5826 * sigma * sqrt(T/m))
    """
    dt = t_years / torch.clamp(num_observations.to(torch.float32), min=1.0)
    factors = 0.5826 * sigmas * torch.sqrt(dt)
    if is_short:
        return barriers * torch.exp(factors)
    else:
        return barriers * torch.exp(-factors)
