"""
engine/cuda/chart_pattern_kernels.py
====================================
OptionAlpha Agent — Module L6: CUDA GPU Kernels for Mass Parallel Candlestick & NR4 Scanning
"""

import torch

def gpu_batch_detect_nr4(
    highs: torch.Tensor,
    lows: torch.Tensor
) -> torch.Tensor:
    """
    Detects NR4 (Narrow Range 4) volatility contraction across thousands of price charts on GPU.
    highs: [Batch, Time]
    lows: [Batch, Time]
    Returns: [Batch] Boolean tensor (1 if NR4, 0 otherwise)
    """
    ranges = highs[:, -4:] - lows[:, -4:] # [Batch, 4]
    current_range = ranges[:, -1:]        # [Batch, 1]
    prior_3_min = torch.min(ranges[:, :3], dim=1, keepdim=True).values
    is_nr4 = (current_range < prior_3_min).squeeze(1).to(torch.int32)
    return is_nr4
