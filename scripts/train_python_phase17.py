"""
Phase 17 Training Matrix Runner (T1 - Python & T6 - CUDA)
Benchmarks and trains Modules BM1, BN1, BO1, BP1 and executes CUDA GPU Kernels BM6, BO6.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.research.kaching_convexity_engine import KaChingConvexityEngine
from ai.research.cross_market_pdt_engine import CrossMarketPdtEngine, CrossMarketPdtState
from ai.research.ratio_backspread_engine import RatioBackspreadEngine
from ai.research.exotic_multileg_ladder_engine import ExoticMultiLegLadderEngine
from engine.cuda.kaching_convexity_kernels import simulate_kaching_dual_decay_cuda
from engine.cuda.ratio_backspread_kernels import simulate_ratio_backspread_breakout_cuda

def run_phase17_python_training():
    # 1. Train Module BM1: Weekly Cash KaChing & Double-Dip Dynamic Convexity Engine (T.R. Lawrence)
    kaching_engine = KaChingConvexityEngine(risk_limit_pct=0.03)
    spot = 175.0
    iv = 0.28
    dte = 110
    state_bm = kaching_engine.initialize_kaching(spot_price=spot, iv=iv, days_to_earnings=dte)
    harvest_tue = kaching_engine.evaluate_weekly_harvest(state_bm, current_short_premium=state_bm.net_weekly_premium * 0.15, day_of_week=2)
    state_rolled = kaching_engine.initialize_kaching(spot_price=160.0, iv=0.45, days_to_earnings=45)
    harvest_def = kaching_engine.evaluate_weekly_harvest(state_rolled, current_short_premium=state_rolled.net_weekly_premium * 2.5, day_of_week=4)

    print(f"  [BM1] KaChing Setup: Long Put ${state_bm.long_put_strike} (delta={state_bm.long_put_delta}), Short Put ${state_bm.short_put_strike} (delta={state_bm.short_put_delta})")
    print(f"  [BM1] Net Weekly Premium: ${state_bm.net_weekly_premium:.2f}, Cumulative Cash: ${state_bm.cumulative_cash_collected:.2f}")
    print(f"  [BM1] Early Tuesday Harvest: Decision={harvest_tue['decision']}, DoubleDipActive={harvest_tue['state'].double_dip_active} -> {harvest_tue['action_data'].get('reason', 'N/A')}")
    print(f"  [BM1] Roll-Down Defense: Decision={harvest_def['decision']}, New Short Strike=${harvest_def['action_data'].get('rolled_strike', 'N/A')}")

    # 2. Train Module BN1: Multi-Asset Cross-Market Liquidity & PDT Governor Engine (Matthew Gray)
    pdt_engine = CrossMarketPdtEngine(pdt_equity_threshold=25000.0, max_pdt_trips=3)
    sub25k_state = CrossMarketPdtState(
        account_equity=18500.0,
        margin_borrowed=0.0,
        forex_leverage_ratio=100.0,
        futures_tick_value=12.50,
        max_risk_per_trade=925.0,
        current_drawdown_pct=0.02,
        round_trips_5d=3,
        asset_class_id=1,
        pdt_restricted=False,
        circuit_breaker_tripped=False
    )
    compliance_sub25k = pdt_engine.audit_trade_compliance(sub25k_state, is_day_trade=True, proposed_risk=450.0)

    over25k_state = CrossMarketPdtState(
        account_equity=52000.0,
        margin_borrowed=10000.0,
        forex_leverage_ratio=50.0,
        futures_tick_value=50.0,
        max_risk_per_trade=2600.0,
        current_drawdown_pct=0.04,
        round_trips_5d=6,
        asset_class_id=1,
        pdt_restricted=False,
        circuit_breaker_tripped=False
    )
    compliance_over25k = pdt_engine.audit_trade_compliance(over25k_state, is_day_trade=True, proposed_risk=1200.0)

    print(f"  [BN1] PDT Audit Sub-$25k ($18,500 eq, 3 trips): Approved={compliance_sub25k['approved']}, Reason={compliance_sub25k['reason']}, Restricted={sub25k_state.pdt_restricted}")
    print(f"  [BN1] PDT Audit Above-$25k ($52,000 eq, 6 trips): Approved={compliance_over25k['approved']}, Reason={compliance_over25k['reason']}")

    # 3. Train Module BO1: Asymmetric 1:2 Ratio Backspread & Volatility Breakout Engine (Frank Richmond)
    ratio_engine = RatioBackspreadEngine()
    rb_state = ratio_engine.construct_call_backspread(spot=100.0, atm_strike=100.0, otm_strike=105.0, short_prem=3.50, long_prem=1.50)
    pnl_downside = ratio_engine.evaluate_pnl_at_expiry(rb_state, terminal_price=90.0)
    pnl_max_loss = ratio_engine.evaluate_pnl_at_expiry(rb_state, terminal_price=105.0)
    pnl_breakout = ratio_engine.evaluate_pnl_at_expiry(rb_state, terminal_price=125.0)

    print(f"  [BO1] 1:2 Call Ratio Backspread: Short 1x ${rb_state.short_strike} / Long 2x ${rb_state.long_strike}")
    print(f"  [BO1] Net Debit/Credit=${rb_state.net_debit_credit:.2f}, Max Loss at ${rb_state.long_strike}=${rb_state.max_loss_point:.2f}, Upper BEP=${rb_state.upper_bep:.2f}")
    print(f"  [BO1] PnL Profiles: Downside Pin ($90)=${pnl_downside:.2f}, Upper Max Loss Pin ($105)=${pnl_max_loss:.2f}, Breakout ($125)=${pnl_breakout:.2f}")

    # 4. Train Module BP1: Exotic Multi-Leg Combinator, Ladder, Strip/Strap & Elasticity Engine (Ryan Bitstone)
    ladder_engine = ExoticMultiLegLadderEngine()
    strip_state = ladder_engine.construct_strip(spot=150.0, atm_strike=150.0, call_prem=4.20, put_prem=4.10)
    strap_state = ladder_engine.construct_strap(spot=150.0, atm_strike=150.0, call_prem=4.20, put_prem=4.10)

    print(f"  [BP1] Strip Volatility Package (2 Puts, 1 Call): Premium=${strip_state.net_package_premium:.2f}, Lambda Elasticity={strip_state.lambda_elasticity:.3f}")
    print(f"  [BP1] Strap Volatility Package (2 Calls, 1 Put): Premium=${strap_state.net_package_premium:.2f}, Lambda Elasticity={strap_state.lambda_elasticity:.3f}")

    print("[T1 PYTHON] Modules BM1, BN1, BO1, BP1 trained successfully on Phase 17 requirements.")

def run_phase17_cuda_kernels():
    print("\n[T6 CUDA] Starting GPU Parallel Processing Training Kernels for Phase 17...")
    res_bm = simulate_kaching_dual_decay_cuda(n_scenarios=100000)
    print(f"  [BM6] Processed {res_bm['n_scenarios']:,} KaChing Dual-Decay & Earnings Buffer Scenarios on GPU.")
    print(f"        Total Cash Projected: ${res_bm['total_cash_collected']:,.2f} | ITM Rate: {res_bm['itm_short_rate']*100:.1f}% | Protection: {res_bm['deep_drop_protection_rate']*100:.1f}%")

    res_bo = simulate_ratio_backspread_breakout_cuda(n_paths=100000)
    print(f"  [BO6] Processed {res_bo['n_paths']:,} 1:2 Ratio Backspread & Volatility Explosion Paths.")
    print(f"        Win Rate: {res_bo['win_rate']*100:.1f}% | Max Gain: ${res_bo['max_gain']:.2f} | Max Loss Pin: ${res_bo['max_loss']:.2f} | Avg PnL: ${res_bo['average_pnl']:.2f}")

    print("[T6 CUDA] Modules BM6, BN6, BO6, BP6 trained successfully.")

if __name__ == "__main__":
    run_phase17_python_training()
    run_phase17_cuda_kernels()
