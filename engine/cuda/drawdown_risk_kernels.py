"""
engine/cuda/drawdown_risk_kernels.py
====================================
OptionAlpha Agent — Module T_sys6: CUDA GPU Kernels for Batch Drawdown & Position Sizing
"""

import torch

def gpu_batch_calculate_position_sizes(
    capital_tensor: torch.Tensor,
    risk_pct_tensor: torch.Tensor,
    max_loss_tensor: torch.Tensor
) -> torch.Tensor:
    """
    Mass GPU batch position sizing:
    Contracts = floor((Capital * (RiskPct / 100)) / MaxLoss)
    """
    dollar_risk = capital_tensor * (risk_pct_tensor / 100.0)
    safe_max_loss = torch.clamp(max_loss_tensor, min=1e-4)
    contracts = torch.floor(dollar_risk / safe_max_loss)
    return torch.clamp(contracts, min=1.0).to(torch.int32)
