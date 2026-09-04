"""
engine/cuda/multi_leg_kernels.py
================================
OptionAlpha Agent — CUDA / Triton GPU Batch Multi-Leg Option Payoff Kernels
Polyglot Pillar 5: CUDA / Triton GPU Acceleration
"""

from __future__ import annotations

import torch


def gpu_batch_iron_condor_payoff(
    spots: torch.Tensor,
    long_puts: torch.Tensor,
    short_puts: torch.Tensor,
    short_calls: torch.Tensor,
    long_calls: torch.Tensor,
    credits: torch.Tensor,
    multiplier: float = 100.0,
) -> torch.Tensor:
    """
    Evaluates millions of 4-leg Iron Condor terminal PnL paths simultaneously on GPU.
    """
    put_spread_loss = torch.clamp(short_puts - spots, min=0.0) - torch.clamp(long_puts - spots, min=0.0)
    call_spread_loss = torch.clamp(spots - short_calls, min=0.0) - torch.clamp(spots - long_calls, min=0.0)
    return (credits - put_spread_loss - call_spread_loss) * multiplier


def gpu_batch_ratio_spread_payoff(
    spots: torch.Tensor,
    long_strikes: torch.Tensor,
    short_strikes: torch.Tensor,
    net_credits: torch.Tensor,
    multiplier: float = 100.0,
) -> torch.Tensor:
    """
    Evaluates 1x2 Put Ratio Spread terminal PnL paths on GPU.
    """
    long_put_val = torch.clamp(long_strikes - spots, min=0.0)
    short_put_val = 2.0 * torch.clamp(short_strikes - spots, min=0.0)
    return (net_credits + long_put_val - short_put_val) * multiplier
