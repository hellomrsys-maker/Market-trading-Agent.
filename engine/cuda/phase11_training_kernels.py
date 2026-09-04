"""
Phase 11 Training Matrix Runner (T6 - CUDA)
Benchmarks and trains CUDA GPU kernels across Modules AO6, AP6, AQ6, AR6.
"""

import numpy as np
from cash_secured_put_kernels import batch_compute_csp_opportunities_cuda
from covered_call_yield_kernels import batch_compute_covered_call_yield_cuda
from wheel_strategy_kernels import batch_compute_wheel_lifecycle_cuda
from retail_income_risk_kernels import batch_audit_retail_income_risk_cuda


def run_phase11_cuda_training():
    print("[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 11...")

    N = 100000

    # 1. Benchmark AO6
    spot_arr = np.random.uniform(50.0, 300.0, N)
    strike_arr = spot_arr * np.random.uniform(0.85, 0.98, N)
    premium_arr = strike_arr * np.random.uniform(0.01, 0.04, N)
    dte_arr = np.random.uniform(15.0, 60.0, N)
    delta_arr = -np.random.uniform(0.10, 0.45, N)

    ao6_res = batch_compute_csp_opportunities_cuda(spot_arr, strike_arr, premium_arr, dte_arr, delta_arr)
    print(f"  [AO6] Processed {N:,} CSP Opportunities on GPU. Avg Annualized ROC: {np.mean(ao6_res[:, 2]):.2f}%, Optimal Setups: {int(np.sum(ao6_res[:, 4])):,}")

    # 2. Benchmark AP6
    stock_basis_arr = spot_arr * np.random.uniform(0.90, 1.10, N)
    cc_strike_arr = spot_arr * np.random.uniform(1.01, 1.15, N)
    call_prem_arr = cc_strike_arr * np.random.uniform(0.01, 0.05, N)
    cc_dte_arr = np.random.uniform(15.0, 60.0, N)
    dividend_arr = np.random.choice([0.0, 0.25, 0.50, 0.75, 1.25], N)

    ap6_res = batch_compute_covered_call_yield_cuda(stock_basis_arr, spot_arr, cc_strike_arr, call_prem_arr, cc_dte_arr, dividend_arr)
    print(f"  [AP6] Processed {N:,} Covered Call Vectors. Avg Max Yield: {np.mean(ap6_res[:, 1]):.2f}%, Early Assignment Alerts: {int(np.sum(ap6_res[:, 3])):,}")

    # 3. Benchmark AQ6
    state_arr = np.random.randint(1, 5, N)
    cost_basis_arr = spot_arr
    accum_income_arr = spot_arr * np.random.uniform(0.02, 0.15, N)
    orig_prem_arr = np.random.uniform(1.0, 5.0, N)
    curr_prem_arr = orig_prem_arr * np.random.uniform(0.1, 0.9, N)

    aq6_res = batch_compute_wheel_lifecycle_cuda(state_arr, spot_arr, cost_basis_arr, accum_income_arr, cc_strike_arr, orig_prem_arr, curr_prem_arr)
    print(f"  [AQ6] Processed {N:,} Wheel Lifecycle States. 50% Profit Targets Hit: {int(np.sum(aq6_res[:, 2])):,}")

    # 4. Benchmark AR6
    equity_arr = np.random.uniform(25000.0, 500000.0, N)
    free_cash_arr = equity_arr * np.random.uniform(0.30, 0.80, N)
    proposed_collateral_arr = equity_arr * np.random.uniform(0.02, 0.08, N)
    existing_collateral_arr = equity_arr * np.random.uniform(0.0, 0.04, N)
    days_earnings_arr = np.random.randint(1, 60, N)

    ar6_res = batch_audit_retail_income_risk_cuda(equity_arr, free_cash_arr, proposed_collateral_arr, existing_collateral_arr, days_earnings_arr)
    print(f"  [AR6] Processed {N:,} Retail Risk Audits. Approved Trades: {int(np.sum(ar6_res[:, 4])):,}")

    print("[T6 CUDA] Modules AO6, AP6, AQ6, AR6 trained successfully.")


if __name__ == "__main__":
    run_phase11_cuda_training()
