"""
engine/cuda/bsm_jump_diffusion_kernels.py
=========================================
OptionAlpha Agent — Module R6: CUDA GPU Kernels for Mass Parallel Black-Scholes-Merton Pricing
"""

import torch

def gpu_batch_bsm_merton_pricing(
    s: torch.Tensor,
    x: torch.Tensor,
    t: torch.Tensor,
    r: torch.Tensor,
    sigma: torch.Tensor,
    q: torch.Tensor
) -> torch.Tensor:
    """
    Mass GPU batch computation of BSM Merton Call Prices & Elasticity across option chains.
    """
    sqrt_t = torch.sqrt(torch.clamp(t, min=1e-6))
    d1 = (torch.log(s / x) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t

    normal = torch.distributions.Normal(0.0, 1.0)
    nd1 = normal.cdf(d1)
    nd2 = normal.cdf(d2)

    exp_qt = torch.exp(-q * t)
    exp_rt = torch.exp(-r * t)

    call_prices = s * exp_qt * nd1 - x * exp_rt * nd2
    call_prices = torch.clamp(call_prices, min=0.0)
    return call_prices
