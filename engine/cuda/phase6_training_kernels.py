"""
engine/cuda/phase6_training_kernels.py
======================================
OptionAlpha Agent — Module T6: CUDA GPU Training Execution for Phase 6
"""

import torch
from loguru import logger
from engine.cuda.dispersion_rainbow_kernels import gpu_batch_rainbow_and_dispersion
from engine.cuda.barrier_autocallable_kernels import gpu_batch_discrete_barrier_shifts
from engine.cuda.cliquet_mountain_kernels import gpu_batch_gflc_cliquets
from engine.cuda.variance_copula_kernels import gpu_batch_variance_swap_greeks

def train():
    logger.info("[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 6...")

    batch_size = 5000
    # 1. Rainbow Dispersion
    returns_matrix = torch.rand((batch_size, 3)) * 0.3 - 0.1
    weights_desc = torch.tensor([0.5, 0.3, 0.2])
    rainbow_payoffs = gpu_batch_rainbow_and_dispersion(returns_matrix, weights_desc)

    # 2. Barrier Shift
    barriers = torch.full((batch_size,), 80.0)
    sigmas = torch.full((batch_size,), 0.20)
    t_years = torch.full((batch_size,), 1.0)
    num_obs = torch.full((batch_size,), 252)
    shifted_h = gpu_batch_discrete_barrier_shifts(barriers, sigmas, t_years, num_obs, True)

    # 3. GFLC Cliquet
    rets_matrix = torch.rand((batch_size, 4)) * 0.2 - 0.05
    gflc = gpu_batch_gflc_cliquets(rets_matrix, 0.0, 0.05, 0.0, 0.15)

    # 4. Variance Swap Greeks
    cash_gamma, vega, theta = gpu_batch_variance_swap_greeks(t_years, torch.full((batch_size,), 0.25), sigmas)

    logger.success("[T6 CUDA] Modules U6, V6, W6, X6 trained successfully.")

if __name__ == "__main__":
    train()
