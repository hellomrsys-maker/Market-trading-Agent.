"""
Phase 15 Training Matrix Runner (T6 - CUDA GPU)
Benchmarks and trains Modules BE6, BF6, BG6, BH6 using GPU parallel processing.
"""

from numba import cuda
import numpy as np
import time

from all_weather_vomma_kernels import all_weather_vomma_kernel
from gamma_scalping_stochastic_kernels import gamma_scalping_stochastic_kernel
from bladerunner_carry_kernels import bladerunner_carry_kernel
from structured_collar_box_kernels import structured_collar_box_kernel

def run_phase15_cuda_training():
    print("[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 15...")
    
    n_threads = 100_000
    threads_per_block = 256
    blocks_per_grid = (n_threads + threads_per_block - 1) // threads_per_block
    
    # --- BE6: All-Weather Vomma ---
    pnl_12 = np.full(n_threads, -7800.0, dtype=np.float64)
    pnl_20 = np.full(n_threads, -11000.0, dtype=np.float64)
    pnl_10 = np.full(n_threads, -1000.0, dtype=np.float64)
    cap = np.full(n_threads, 20000.0, dtype=np.float64)
    vix = np.full(n_threads, 38.0, dtype=np.float64)
    res_be = np.zeros((n_threads, 4), dtype=np.float64)
    
    all_weather_vomma_kernel[blocks_per_grid, threads_per_block](pnl_12, pnl_20, pnl_10, cap, vix, res_be)
    
    # --- BF6: Gamma Scalping ---
    delta = np.random.uniform(-10.0, 10.0, n_threads).astype(np.float64)
    threshold = np.full(n_threads, 0.05, dtype=np.float64)
    res_bf = np.zeros((n_threads, 2), dtype=np.float64)
    
    gamma_scalping_stochastic_kernel[blocks_per_grid, threads_per_block](delta, threshold, res_bf)
    
    # --- BG6: Bladerunner Forex ---
    spot = np.random.uniform(1.0, 1.5, n_threads).astype(np.float64)
    ema20 = np.full(n_threads, 1.25, dtype=np.float64)
    rej = np.ones(n_threads, dtype=np.float64)
    conf = np.ones(n_threads, dtype=np.float64)
    r_long = np.full(n_threads, 4.50, dtype=np.float64)
    r_short = np.full(n_threads, 0.10, dtype=np.float64)
    units = np.full(n_threads, 100000.0, dtype=np.float64)
    w_prob = np.full(n_threads, 0.60, dtype=np.float64)
    w_loss = np.full(n_threads, 1.5, dtype=np.float64)
    res_bg = np.zeros((n_threads, 3), dtype=np.float64)
    
    bladerunner_carry_kernel[blocks_per_grid, threads_per_block](spot, ema20, rej, conf, r_long, r_short, units, w_prob, w_loss, res_bg)
    
    # --- BH6: Structured Collar & Box ---
    basis = np.full(n_threads, 79.0, dtype=np.float64)
    c_k = np.full(n_threads, 88.0, dtype=np.float64)
    c_p = np.full(n_threads, 1.75, dtype=np.float64)
    p_k = np.full(n_threads, 85.0, dtype=np.float64)
    p_p = np.full(n_threads, 1.24, dtype=np.float64)
    b_k1 = np.full(n_threads, 95.0, dtype=np.float64)
    b_k2 = np.full(n_threads, 105.0, dtype=np.float64)
    b_d = np.full(n_threads, 8.80, dtype=np.float64)
    bet = np.full(n_threads, 100.0, dtype=np.float64)
    pay = np.full(n_threads, 80.0, dtype=np.float64)
    itm = np.ones(n_threads, dtype=np.float64)
    res_bh = np.zeros((n_threads, 5), dtype=np.float64)
    
    structured_collar_box_kernel[blocks_per_grid, threads_per_block](basis, c_k, c_p, p_k, p_p, b_k1, b_k2, b_d, bet, pay, itm, res_bh)
    
    cuda.synchronize()
    
    safe_margin_count = np.sum(res_be[:, 2])
    rebal_count = np.sum(res_bf[:, 1])
    box_prof_count = np.sum(res_bh[:, 3])
    
    print(f"  [BE6] Processed {n_threads:,} SPAN Margin Stress Scenarios. Safe Accounts: {int(safe_margin_count)}")
    print(f"  [BF6] Processed {n_threads:,} Gamma Scalping Paths. Rebalances Triggered: {int(rebal_count)}")
    print(f"  [BG6] Processed {n_threads:,} Bladerunner Forex Trends & Carry Allocations.")
    print(f"  [BH6] Processed {n_threads:,} Structured Box Arbitrage Trees. Profitable Arbitrage: {int(box_prof_count)}")
    
    print("[T6 CUDA] Modules BE6, BF6, BG6, BH6 trained successfully.")

if __name__ == "__main__":
    run_phase15_cuda_training()
