"""
engine/cuda/stop_loss_kernels.py
================================
OptionAlpha Agent — Module K6: CUDA GPU Kernels for Mass Stop Loss Monitoring
"""

import torch

def gpu_batch_check_stops(
    prices: torch.Tensor,
    stops: torch.Tensor,
    is_long: torch.Tensor
) -> torch.Tensor:
    """
    Checks stop loss breaches across millions of positions concurrently on GPU.
    """
    long_breached = (is_long == 1) & (prices <= stops)
    short_breached = (is_long == 0) & (prices >= stops)
    return (long_breached | short_breached).to(torch.int32)
