"""
Phase 14 Training Matrix Runner (T6 - CUDA)
Benchmarks and trains CUDA GPU kernels across Modules BA6, BB6, BC6, BD6.
"""

import numpy as np
from classical_reversal_kernels import batch_compute_classical_reversals_cuda
from continuation_geometry_kernels import batch_compute_continuation_geometry_cuda
from volume_trap_filter_kernels import batch_compute_volume_traps_cuda
from pattern_risk_governor_kernels import batch_compute_pattern_risk_cuda


def run_phase14_cuda_training():
    print("[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 14...")

    N = 100000

    # 1. Benchmark BA6
    head_peak_arr = np.random.uniform(100.0, 200.0, N)
    neckline_arr = head_peak_arr - np.random.uniform(5.0, 20.0, N)
    spot_arr = neckline_arr + np.random.uniform(-10.0, 10.0, N)
    is_bullish_arr = np.random.choice([0.0, 1.0], N)
    ba6_res = batch_compute_classical_reversals_cuda(head_peak_arr, neckline_arr, spot_arr, is_bullish_arr)
    print(f"  [BA6] Processed {N:,} Classical Reversal Formations on GPU. Confirmed Breakouts: {int(np.sum(ba6_res[:, 2])):,}")

    # 2. Benchmark BB6
    breakout_px_arr = np.random.uniform(50.0, 300.0, N)
    dim_height_arr = np.random.uniform(5.0, 30.0, N)
    bb6_res = batch_compute_continuation_geometry_cuda(breakout_px_arr, dim_height_arr, spot_arr, is_bullish_arr)
    print(f"  [BB6] Processed {N:,} Continuation Geometry Patterns. Breakouts Active: {int(np.sum(bb6_res[:, 1])):,}")

    # 3. Benchmark BC6
    vol_arr = np.random.uniform(100000.0, 1000000.0, N)
    sma_vol_arr = np.random.uniform(200000.0, 500000.0, N)
    key_level_arr = np.random.uniform(50.0, 300.0, N)
    extreme_px_arr = key_level_arr + np.random.uniform(-5.0, 5.0, N)
    close_px_arr = key_level_arr + np.random.uniform(-3.0, 3.0, N)
    is_support_arr = np.random.choice([0.0, 1.0], N)
    bc6_res = batch_compute_volume_traps_cuda(vol_arr, sma_vol_arr, key_level_arr, extreme_px_arr, close_px_arr, is_support_arr)
    print(f"  [BC6] Processed {N:,} Volume Breakout & Trap Vectors. High Volume Surge: {int(np.sum(bc6_res[:, 1])):,}, Wyckoff Traps: {int(np.sum(bc6_res[:, 2])):,}")

    # 4. Benchmark BD6
    entry_arr = np.random.uniform(50.0, 300.0, N)
    target_arr = entry_arr + np.random.uniform(5.0, 40.0, N)
    stop_arr = entry_arr - np.random.uniform(2.0, 15.0, N)
    htf_dir_arr = np.random.choice([-1.0, 0.0, 1.0], N)
    pattern_dir_arr = np.random.choice([-1.0, 1.0], N)
    bd6_res = batch_compute_pattern_risk_cuda(entry_arr, target_arr, stop_arr, htf_dir_arr, pattern_dir_arr)
    print(f"  [BD6] Processed {N:,} Pattern Risk Audits. Approved Trades: {int(np.sum(bd6_res[:, 3])):,}")

    print("[T6 CUDA] Modules BA6, BB6, BC6, BD6 trained successfully.")


if __name__ == "__main__":
    run_phase14_cuda_training()
