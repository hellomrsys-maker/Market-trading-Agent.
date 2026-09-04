"""
engine/cuda/cognitive_bias_kernels.py
=====================================
OptionAlpha Agent — Module P6: CUDA GPU Kernels for Mass Bias & Journal Log Processing
"""

import torch

def gpu_batch_audit_intervals(
    time_since_loss_tensor: torch.Tensor,
    stress_scores: torch.Tensor
) -> torch.Tensor:
    """
    Evaluates emotional circuit breakers across all trading streams on GPU:
    1 = Trade Allowed (Cooldown >= 30m and Stress <= 6)
    0 = Blocked by Circuit Breaker
    """
    cooldown_ok = time_since_loss_tensor >= 30
    stress_ok = stress_scores <= 6
    return (cooldown_ok & stress_ok).to(torch.int32)
