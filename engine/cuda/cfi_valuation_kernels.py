"""
engine/cuda/cfi_valuation_kernels.py
====================================
OptionAlpha Agent — Module O6: CUDA GPU Kernels for Mass Intrinsic Valuation Screening
"""

import torch

def gpu_batch_graham_number(
    eps_tensor: torch.Tensor,
    bvps_tensor: torch.Tensor
) -> torch.Tensor:
    """
    Computes Ben Graham Numbers across millions of equities concurrently on GPU:
    sqrt(22.5 * EPS * BVPS)
    """
    valid_mask = (eps_tensor > 0.0) & (bvps_tensor > 0.0)
    graham_values = torch.zeros_like(eps_tensor)
    graham_values[valid_mask] = torch.sqrt(22.5 * eps_tensor[valid_mask] * bvps_tensor[valid_mask])
    return graham_values
