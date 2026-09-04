"""
Phase 13 Training Matrix Runner (T6 - CUDA)
Benchmarks and trains CUDA GPU kernels across Modules AW6, AX6, AY6, AZ6.
"""

import numpy as np
from volatility_edge_discovery_kernels import batch_compute_volatility_edge_cuda
from trading_firm_greek_kernels import batch_compute_greek_governance_cuda
from volatility_skew_kernels import batch_compute_volatility_skew_cuda
from trade_adjustment_kernels import batch_compute_trade_defense_cuda


def run_phase13_cuda_training():
    print("[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 13...")

    N = 100000

    # 1. Benchmark AW6
    iv_arr = np.random.uniform(12.0, 45.0, N)
    hv_arr = np.random.uniform(10.0, 40.0, N)
    min_iv_arr = np.random.uniform(8.0, 15.0, N)
    max_iv_arr = np.random.uniform(40.0, 65.0, N)
    aw6_res = batch_compute_volatility_edge_cuda(iv_arr, hv_arr, min_iv_arr, max_iv_arr)
    print(f"  [AW6] Processed {N:,} Volatility Edge Vectors on GPU. Expensive Vol Setups: {int(np.sum(aw6_res[:, 2])):,}, Cheap Vol Setups: {int(np.sum(aw6_res[:, 3])):,}")

    # 2. Benchmark AX6
    delta_arr = np.random.uniform(-80.0, 80.0, N)
    gamma_arr = np.random.uniform(0.01, 0.10, N)
    theta_arr = -np.random.uniform(10.0, 60.0, N)
    vega_arr = np.random.uniform(10.0, 90.0, N)
    spot_arr = np.random.uniform(50.0, 300.0, N)
    equity_arr = np.random.uniform(50000.0, 500000.0, N)
    ax6_res = batch_compute_greek_governance_cuda(delta_arr, gamma_arr, theta_arr, vega_arr, spot_arr, iv_arr, equity_arr)
    print(f"  [AX6] Processed {N:,} Greek Inventory Audits. Compliant Portfolios: {int(np.sum(ax6_res[:, 3])):,}")

    # 3. Benchmark AY6
    iv_atm_arr = np.random.uniform(15.0, 35.0, N)
    iv_put25_arr = iv_atm_arr * np.random.uniform(1.05, 1.40, N)
    iv_call25_arr = iv_atm_arr * np.random.uniform(0.85, 1.10, N)
    iv_30_arr = iv_atm_arr
    iv_90_arr = iv_atm_arr * np.random.uniform(0.95, 1.20, N)
    c1_arr = np.random.uniform(1.0, 3.0, N)
    c2_arr = np.random.uniform(2.0, 4.5, N)
    c3_arr = np.random.uniform(2.5, 6.0, N)
    k1_arr = spot_arr * 0.90
    k2_arr = spot_arr * 0.95
    ay6_res = batch_compute_volatility_skew_cuda(iv_atm_arr, iv_put25_arr, iv_call25_arr, iv_30_arr, iv_90_arr, c1_arr, c2_arr, c3_arr, k1_arr, k2_arr)
    print(f"  [AY6] Processed {N:,} Skew & BWB Structures. Steep Put Skew: {int(np.sum(ay6_res[:, 2])):,}, Zero Downside Risk BWBs: {int(np.sum(ay6_res[:, 4])):,}")

    # 4. Benchmark AZ6
    credit_arr = np.random.uniform(100.0, 500.0, N)
    pnl_arr = np.random.uniform(-800.0, 400.0, N)
    short_delta_arr = -np.random.uniform(0.10, 0.60, N)
    dte_arr = np.random.uniform(1.0, 45.0, N)
    extrinsic_arr = np.random.uniform(0.05, 1.50, N)
    az6_res = batch_compute_trade_defense_cuda(pnl_arr, credit_arr, short_delta_arr, dte_arr, extrinsic_arr)
    print(f"  [AZ6] Processed {N:,} Trade Defense Audits. Wing Adjustments: {int(np.sum(az6_res[:, 2] == 2.0)):,}, Cut Loss Directives: {int(np.sum(az6_res[:, 2] == 1.0)):,}")

    print("[T6 CUDA] Modules AW6, AX6, AY6, AZ6 trained successfully.")


if __name__ == "__main__":
    run_phase13_cuda_training()
