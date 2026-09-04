"""
engine/cuda/dispersion_rainbow_kernels.py
=========================================
OptionAlpha Agent — Module U6: CUDA GPU Kernels for Basket Dispersion & Rainbow Options
"""

import torch

def gpu_batch_rainbow_and_dispersion(
    returns_matrix: torch.Tensor, # Shape: (batch_size, n_assets)
    weights_desc: torch.Tensor    # Shape: (n_assets,)
) -> torch.Tensor:
    """
    Mass GPU batch computation:
    Sorts returns across assets for 10,000+ baskets simultaneously and computes Rainbow payoff.
    """
    sorted_returns, _ = torch.sort(returns_matrix, dim=-1, descending=True)
    rainbow_payoffs = torch.matmul(sorted_returns, weights_desc)
    return torch.clamp(rainbow_payoffs, min=0.0)
