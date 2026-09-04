"""
engine/cuda/order_flow_footprint_kernels.py
===========================================
OptionAlpha Agent — Module I6: CUDA GPU Kernels for High-Throughput Footprint & VPOC Scanning
"""

import torch

def gpu_batch_footprint_delta(
    ask_matrix: torch.Tensor,
    bid_matrix: torch.Tensor
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Computes bar deltas and cumulative delta across thousands of symbols simultaneously on GPU.
    ask_matrix: [Batch, Levels]
    bid_matrix: [Batch, Levels]
    Returns: (bar_deltas [Batch], cumulative_deltas [Batch])
    """
    total_asks = torch.sum(ask_matrix, dim=1)
    total_bids = torch.sum(bid_matrix, dim=1)
    bar_deltas = total_asks - total_bids
    cum_deltas = torch.cumsum(bar_deltas, dim=0)
    return bar_deltas, cum_deltas

def gpu_batch_vpoc_finder(
    price_levels: torch.Tensor,
    volume_matrix: torch.Tensor
) -> torch.Tensor:
    """
    Finds the Volume Point of Control (VPOC) strike/price for batched volume profiles.
    price_levels: [Batch, Levels]
    volume_matrix: [Batch, Levels]
    Returns: [Batch] VPOC prices
    """
    max_indices = torch.argmax(volume_matrix, dim=1, keepdim=True)
    vpoc_prices = torch.gather(price_levels, 1, max_indices).squeeze(1)
    return vpoc_prices
