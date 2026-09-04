"""
engine/cuda/option_buying_kernels.py
====================================
OptionAlpha Agent — Module J6: CUDA GPU Kernels for Batch Option Buying Valuation & Theta Decay
"""

import torch

def gpu_batch_option_buyer_milestone_sl(
    entry_prices: torch.Tensor,
    current_prices: torch.Tensor,
    t1_targets: torch.Tensor,
    t2_targets: torch.Tensor,
    initial_sls: torch.Tensor
) -> torch.Tensor:
    """
    Computes trailing stop-loss values for millions of option contracts concurrently on GPU.
    """
    active_stops = initial_sls.clone()
    
    # Target 1 reached -> Move SL to Cost
    t1_mask = current_prices >= t1_targets
    active_stops[t1_mask] = entry_prices[t1_mask]
    
    # Target 2 reached -> Move SL to Target 1
    t2_mask = current_prices >= t2_targets
    active_stops[t2_mask] = t1_targets[t2_mask]
    
    return active_stops
