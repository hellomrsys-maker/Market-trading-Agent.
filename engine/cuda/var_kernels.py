"""
engine/cuda/var_kernels.py
==========================
OptionAlpha Agent — CUDA / Triton GPU Accelerated 99% Delta-Gamma VaR & CVaR Engine
Polyglot Pillar 5: CUDA / Triton GPU Acceleration
"""

from __future__ import annotations

import torch


def gpu_batch_delta_gamma_var(
    delta_vector: torch.Tensor,
    gamma_vector: torch.Tensor,
    vega_vector: torch.Tensor,
    simulated_spot_returns: torch.Tensor, # [N_paths, N_assets]
    simulated_vol_shocks: torch.Tensor,   # [N_paths, N_assets]
    portfolio_equity: float = 100000.0,
) -> tuple[float, float, float]:
    """
    Simulates 100,000 parallel portfolio PnL trajectories on GPU VRAM:
      PnL_path = sum_i [ Delta_i * dS_i + 0.5 * Gamma_i * dS_i^2 + Vega_i * dVol_i * 100 ]
    """
    # [N_paths, N_assets] * [N_assets] -> [N_paths]
    delta_pnl = torch.matmul(simulated_spot_returns, delta_vector)
    gamma_pnl = 0.5 * torch.matmul(simulated_spot_returns ** 2, gamma_vector)
    vega_pnl = torch.matmul(simulated_vol_shocks * 100.0, vega_vector)

    total_path_pnls = delta_pnl + gamma_pnl + vega_pnl

    # Sort PnLs on GPU
    sorted_pnls, _ = torch.sort(total_path_pnls)
    n_paths = sorted_pnls.shape[0]

    # 99% VaR (1st percentile)
    var_idx = int(0.01 * n_paths)
    var_99_dollars = -float(sorted_pnls[var_idx].item())
    var_99_pct = (var_99_dollars / portfolio_equity) * 100.0

    # 99% CVaR (Expected shortfall below 1st percentile)
    cvar_99_dollars = -float(torch.mean(sorted_pnls[:var_idx]).item())

    return var_99_dollars, var_99_pct, cvar_99_dollars
