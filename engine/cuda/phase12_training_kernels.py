"""
Phase 12 Training Matrix Runner (T6 - CUDA)
Benchmarks and trains CUDA GPU kernels across Modules AS6, AT6, AU6, AV6.
"""

import numpy as np
from commodity_specs_margin_kernels import batch_compute_margin_health_cuda
from delivery_roll_governor_kernels import batch_compute_delivery_rolls_cuda
from commodity_seasonality_kernels import batch_compute_seasonality_cuda
from cash_futures_basis_kernels import batch_compute_cash_futures_basis_cuda


def run_phase12_cuda_training():
    print("[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 12...")

    N = 100000

    # 1. Benchmark AS6
    equity_arr = np.random.uniform(25000.0, 500000.0, N)
    initial_margin_arr = equity_arr * np.random.uniform(0.10, 0.60, N)
    maint_margin_arr = initial_margin_arr * 0.90
    as6_res = batch_compute_margin_health_cuda(equity_arr, initial_margin_arr, maint_margin_arr)
    print(f"  [AS6] Processed {N:,} SPAN Margin Audits on GPU. Avg Margin Excess: ${np.mean(as6_res[:, 0]):.2f}, Margin Calls: {int(np.sum(as6_res[:, 4])):,}")

    # 2. Benchmark AT6
    is_physical_arr = np.random.choice([0.0, 1.0], N, p=[0.3, 0.7])
    days_fnd_arr = np.random.randint(1, 30, N)
    vol_m1_arr = np.random.uniform(10000, 200000, N)
    vol_m2_arr = np.random.uniform(10000, 200000, N)
    at6_res = batch_compute_delivery_rolls_cuda(is_physical_arr, days_fnd_arr, vol_m1_arr, vol_m2_arr)
    print(f"  [AT6] Processed {N:,} Delivery Risk Vectors. Roll Directives: {int(np.sum(at6_res[:, 2] == 1.0)):,}, Forced Liquidations: {int(np.sum(at6_res[:, 2] == 2.0)):,}")

    # 3. Benchmark AU6
    base_scores = np.random.uniform(-0.8, 0.8, N)
    weather_severities = np.random.uniform(0.0, 1.0, N)
    old_crop_prices = np.random.uniform(400.0, 1500.0, N)
    new_crop_prices = old_crop_prices + np.random.uniform(-50.0, 50.0, N)
    au6_res = batch_compute_seasonality_cuda(base_scores, weather_severities, old_crop_prices, new_crop_prices)
    print(f"  [AU6] Processed {N:,} Seasonality Vectors. Bull Season Windows: {int(np.sum(au6_res[:, 1] == 1.0)):,}, Inversions: {int(np.sum(au6_res[:, 3] == 1.0)):,}")

    # 4. Benchmark AV6
    cash_prices = np.random.uniform(50.0, 100.0, N)
    futures_prices = cash_prices + np.random.uniform(-5.0, 5.0, N)
    basis_means = np.full(N, 0.10)
    basis_stds = np.full(N, 0.50)
    carrying_costs = np.random.uniform(1.0, 4.0, N)
    av6_res = batch_compute_cash_futures_basis_cuda(cash_prices, futures_prices, basis_means, basis_stds, carrying_costs)
    print(f"  [AV6] Processed {N:,} Basis Arbitrage Vectors. Profitable Cash & Carry: {int(np.sum(av6_res[:, 4])):,}")

    print("[T6 CUDA] Modules AS6, AT6, AU6, AV6 trained successfully.")


if __name__ == "__main__":
    run_phase12_cuda_training()
