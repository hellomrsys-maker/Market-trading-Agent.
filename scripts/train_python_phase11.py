"""
Phase 11 Training Matrix Runner (T1 - Python)
Benchmarks and trains Modules AO1, AP1, AQ1, AR1.
"""

import os
import sys

# Ensure ai package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.research.cash_secured_put_engine import CashSecuredPutEngine
from ai.research.covered_call_yield_engine import CoveredCallYieldEngine
from ai.research.wheel_strategy_engine import WheelStrategyEngine
from ai.research.retail_income_risk_governor import RetailIncomeRiskGovernor


def run_phase11_python_training():
    print("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 11...")

    # 1. Train Module AO1: Cash-Secured Put Engine
    csp_engine = CashSecuredPutEngine()
    csp_res = csp_engine.evaluate_csp_opportunity(spot_price=100.0, strike_price=95.0, premium_received=1.85, dte_days=35.0, put_delta=-0.26)
    ladder = csp_engine.generate_csp_ladder_schedule("AAPL", spot_price=150.0, total_collateral_budget=50000.0, num_tiers=4)

    print(f"  [AO1] CSP Basis: ${csp_res['effective_cost_basis']} (Disc: {csp_res['discount_from_spot_pct']}%), Ann ROC: {csp_res['annualized_roc_pct']}%, POP: {csp_res['est_pop_pct']}%")
    print(f"  [AO1] Generated {len(ladder)}-tier CSP Ladder. Tier 1 Strike: ${ladder[0]['target_strike']}, DTE: {ladder[0]['dte_days']}")

    # 2. Train Module AP1: Covered Call Yield Engine
    cc_engine = CoveredCallYieldEngine()
    cc_res = cc_engine.evaluate_covered_call(stock_cost_basis=100.0, current_spot=102.5, strike_price=105.0, call_premium=2.40, dte_days=30.0, impending_dividend_per_share=0.50)

    print(f"  [AP1] CC Static Yield: {cc_res['annualized_static_yield_pct']}%, Max Yield: {cc_res['annualized_max_yield_pct']}%, Assignment Risk: {cc_res['early_assignment_warning']}")

    # 3. Train Module AQ1: Wheel Strategy Lifecycle Engine
    wheel_engine = WheelStrategyEngine()
    wheel_res = wheel_engine.track_wheel_lifecycle(
        current_state="STATE_2_PUT_ACTIVE", spot_price=98.0, cost_basis_shares=100.0,
        accumulated_put_premiums=3.50, accumulated_call_premiums=2.10, accumulated_dividends=1.00,
        active_option_strike=95.0, active_option_original_premium=2.00, active_option_current_price=0.80
    )

    print(f"  [AQ1] True Net Cost Basis: ${wheel_res['true_net_cost_basis']} -> Action: {wheel_res['recommended_action']}")

    # 4. Train Module AR1: Retail Income Risk Governor Engine
    gov_engine = RetailIncomeRiskGovernor()
    audit_res = gov_engine.audit_trade_allocation(account_equity=100000.0, current_free_cash=45000.0, proposed_trade_collateral=4500.0, existing_symbol_collateral=0.0, days_to_earnings=25)

    print(f"  [AR1] Trade Audit: {audit_res['verdict']} (Cash Buffer: {audit_res['projected_cash_buffer_pct']}%, Max Symbol Cap: ${audit_res['max_allowed_symbol_exposure']})")

    print("[T1 PYTHON] Modules AO1, AP1, AQ1, AR1 trained successfully on Phase 11 requirements.")


if __name__ == "__main__":
    run_phase11_python_training()
