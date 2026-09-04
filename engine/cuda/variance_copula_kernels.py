"""
engine/cuda/variance_copula_kernels.py
======================================
OptionAlpha Agent — Module X6: CUDA GPU Kernels for Variance Swap Greeks & Copula Simulation
"""

import torch

def gpu_batch_variance_swap_greeks(
    t_years: torch.Tensor,
    time_elapsed: torch.Tensor,
    sigmas: torch.Tensor
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Mass GPU batch calculation of Demeterfi et al. (1999) Variance Swap Greeks:
    Cash Gamma = 2/T, Vega = (2/T)*sigma*(T-t), Theta = -(1/T)*sigma^2
    """
    t_safe = torch.clamp(t_years, min=1e-4)
    t_rem = torch.clamp(t_years - time_elapsed, min=1e-4)

    cash_gammas = 2.0 / t_safe
    vegas = (2.0 / t_safe) * sigmas * t_rem
    thetas = - (1.0 / t_safe) * (sigmas ** 2)

    return cash_gammas, vegas, thetas
