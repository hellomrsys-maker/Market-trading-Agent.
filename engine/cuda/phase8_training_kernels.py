"""
Phase 8 Training Matrix Runner (T6 - CUDA)
Benchmarks and trains CUDA GPU kernels across Modules AC6, AD6, AE6, AF6.
"""

import numpy as np
from options_equivalency_kernels import batch_evaluate_put_call_parity_cuda, batch_evaluate_box_spreads_cuda
from second_order_greeks_kernels import batch_forward_volatility_cuda
from multidimensional_spread_kernels import batch_ratio_spread_cuda, batch_backspread_cuda
from strategic_gamma_kernels import batch_gamma_decay_breakeven_cuda, batch_daily_sigma_moves_cuda


def train_phase8_cuda():
    print("[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 8...")

    # AC6 Batch
    spots = np.array([66.0, 100.0, 150.0], dtype=np.float32)
    strikes = np.array([65.0, 100.0, 145.0], dtype=np.float32)
    calls = np.array([3.45, 5.00, 10.00], dtype=np.float32)
    puts = np.array([2.10, 4.50, 4.00], dtype=np.float32)
    bases = np.array([0.35, 0.50, 1.00], dtype=np.float32)
    ac_res = batch_evaluate_put_call_parity_cuda(spots, strikes, calls, puts, bases)

    # AD6 Batch
    v_near = np.array([0.36, 0.20, 0.40], dtype=np.float32)
    d_near = np.array([30, 20, 15], dtype=np.int32)
    v_def = np.array([0.54, 0.25, 0.45], dtype=np.float32)
    d_def = np.array([90, 60, 45], dtype=np.int32)
    ad_res = batch_forward_volatility_cuda(v_near, d_near, v_def, d_def)

    # AE6 Batch
    k1 = np.array([50.0, 90.0], dtype=np.float32)
    k2 = np.array([55.0, 100.0], dtype=np.float32)
    p_long = np.array([4.0, 4.0], dtype=np.float32)
    p_short = np.array([2.0, 10.5], dtype=np.float32)
    ae_res = batch_ratio_spread_cuda(k1, k2, p_long, p_short)

    # AF6 Batch
    thetas = np.array([0.03, 0.05, 0.08], dtype=np.float32)
    gammas = np.array([0.15, 0.10, 0.20], dtype=np.float32)
    af_res = batch_gamma_decay_breakeven_cuda(thetas, gammas)

    print("[T6 CUDA] Modules AC6, AD6, AE6, AF6 trained successfully.")


if __name__ == "__main__":
    train_phase8_cuda()
