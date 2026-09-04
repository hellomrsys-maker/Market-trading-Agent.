"""
engine/cuda/order_flow_kernels.py
=================================
OptionAlpha Agent — CUDA GPU Kernels for Options Chain Open Interest Tracking
Polyglot Pillar 5: CUDA / Triton GPU Acceleration
MASTER MANDATE & POLYGLOT COMPUTING RULE APPLIED
"""

from __future__ import annotations
import torch

def gpu_batch_oi_trend_classifier(
    price_trends: torch.Tensor,
    oi_trends: torch.Tensor,
    volume_trends: torch.Tensor
) -> torch.Tensor:
    """
    GPU Batch OI & Volume Classification:
    1 = LONG_BUILDUP
    2 = SHORT_COVERING
    3 = SHORT_BUILDUP
    4 = LONG_UNWINDING
    0 = NEUTRAL
    All tensors should be +1 for rising, -1 for falling.
    """
    actions = torch.zeros_like(price_trends, dtype=torch.int32)
    
    long_buildup = (price_trends == 1) & (oi_trends == 1) & (volume_trends == 1)
    short_covering = (price_trends == 1) & (oi_trends == -1) & (volume_trends == -1)
    short_buildup = (price_trends == -1) & (oi_trends == 1) & (volume_trends == 1)
    long_unwinding = (price_trends == -1) & (oi_trends == -1) & (volume_trends == -1)
    
    actions[long_buildup] = 1
    actions[short_covering] = 2
    actions[short_buildup] = 3
    actions[long_unwinding] = 4
    
    return actions

def gpu_batch_max_pain_scan(
    strikes: torch.Tensor,
    call_oi: torch.Tensor,
    put_oi: torch.Tensor
) -> torch.Tensor:
    """
    Computes Max Pain concurrently for a massive matrix of options chains.
    strikes: [B, N]
    call_oi: [B, N]
    put_oi: [B, N]
    Returns: [B] (The Max Pain strike per chain)
    """
    B, N = strikes.shape
    pain_matrix = torch.zeros((B, N), device=strikes.device)
    
    # Brute force vectorized max pain computation
    for i in range(N):
        test_strike = strikes[:, i].unsqueeze(1) # [B, 1]
        
        # Call pain: max(0, test_strike - strike) * call_oi
        call_pain = torch.clamp(test_strike - strikes, min=0.0) * call_oi
        # Put pain: max(0, strike - test_strike) * put_oi
        put_pain = torch.clamp(strikes - test_strike, min=0.0) * put_oi
        
        total_pain = torch.sum(call_pain + put_pain, dim=1) # [B]
        pain_matrix[:, i] = total_pain
        
    min_pain_indices = torch.argmin(pain_matrix, dim=1)
    # Gather the strikes at those indices
    return torch.gather(strikes, 1, min_pain_indices.unsqueeze(1)).squeeze(1)
