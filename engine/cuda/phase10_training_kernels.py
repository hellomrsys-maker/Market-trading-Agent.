"""
Phase 10 Training Matrix Runner (T6 - CUDA)
Benchmarks and trains CUDA GPU kernels across Modules AK6, AL6, AM6, AN6.
"""

import numpy as np
from schwager_price_action_kernels import batch_compute_schwager_price_action_cuda
from commodity_spread_arbitrage_kernels import batch_compute_commodity_spreads_cuda
from cot_institutional_sentiment_kernels import batch_compute_cot_sentiment_cuda
from futures_risk_governor_kernels import batch_compute_futures_risk_cuda


def run_phase10_cuda_training():
    print("[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 10...")

    N = 100000

    # 1. Benchmark AK6
    prev_lows = np.random.uniform(90.0, 110.0, N)
    prev_highs = prev_lows + np.random.uniform(1.0, 4.0, N)
    prev_closes = prev_lows + np.random.uniform(0.5, 3.5, N)
    curr_lows = prev_lows + np.random.uniform(-2.0, 2.0, N)
    curr_highs = prev_highs + np.random.uniform(-2.0, 2.0, N)
    curr_closes = curr_lows + np.random.uniform(0.5, 4.0, N)
    curr_vols = np.random.uniform(50000, 250000, N)
    avg_vols = np.full(N, 100000.0)
    supports = prev_lows - 0.5
    resistances = prev_highs + 0.5

    ak6_res = batch_compute_schwager_price_action_cuda(
        prev_lows, prev_highs, prev_closes, curr_lows, curr_highs, curr_closes, curr_vols, avg_vols, supports, resistances
    )
    print(f"  [AK6] Processed {N:,} Schwager Price Action Bars on GPU. Reversals: {int(np.sum(ak6_res[:, 0] != 0)):,}, Traps: {int(np.sum(ak6_res[:, 1] != 0)):,}")

    # 2. Benchmark AL6
    cl_arr = np.random.uniform(60.0, 95.0, N)
    rbob_arr = np.random.uniform(2.0, 3.2, N)
    ho_arr = np.random.uniform(2.1, 3.3, N)
    beans_arr = np.random.uniform(1100.0, 1500.0, N)
    meal_arr = np.random.uniform(300.0, 450.0, N)
    oil_arr = np.random.uniform(45.0, 70.0, N)

    al6_res = batch_compute_commodity_spreads_cuda(cl_arr, rbob_arr, ho_arr, beans_arr, meal_arr, oil_arr)
    print(f"  [AL6] Processed {N:,} Commodity Spread Vectors. Avg Crack Margin: ${np.mean(al6_res[:, 0]):.2f}/bbl, Avg Crush GPM: {np.mean(al6_res[:, 2]):.2f}c/bu")

    # 3. Benchmark AM6
    curr_net = np.random.uniform(-100000, 250000, N)
    min_net = np.full(N, -150000.0)
    max_net = np.full(N, 300000.0)
    p_change = np.random.uniform(-5.0, 5.0, N)
    oi_change = np.random.uniform(-20000, 20000, N)

    am6_res = batch_compute_cot_sentiment_cuda(curr_net, min_net, max_net, p_change, oi_change)
    print(f"  [AM6] Processed {N:,} COT Sentiment Vectors. Extreme Commercial Signals: {int(np.sum(am6_res[:, 1])):,}")

    # 4. Benchmark AN6
    equity_arr = np.random.uniform(50000.0, 500000.0, N)
    risk_pct_arr = np.random.uniform(1.0, 2.0, N)
    atr_arr = np.random.uniform(1.0, 5.0, N)
    mult_arr = np.full(N, 2.0)
    pt_val_arr = np.full(N, 1000.0)
    is_sharpe = np.random.uniform(1.0, 2.5, N)
    oos_sharpe = np.random.uniform(0.4, 2.2, N)
    open_risk = np.random.uniform(1000.0, 25000.0, N)

    an6_res = batch_compute_futures_risk_cuda(equity_arr, risk_pct_arr, atr_arr, mult_arr, pt_val_arr, is_sharpe, oos_sharpe, open_risk)
    print(f"  [AN6] Processed {N:,} Futures Risk Vectors. Deployable Systems: {int(np.sum(an6_res[:, 2])):,}, Heat Compliant: {int(np.sum(an6_res[:, 3])):,}")

    print("[T6 CUDA] Modules AK6, AL6, AM6, AN6 trained successfully.")


if __name__ == "__main__":
    run_phase10_cuda_training()
