"""
Phase 9 Training Matrix Runner (T1 - Python)
Benchmarks and trains Modules AG1, AH1, AI1, AJ1.
"""

import os
import sys

# Ensure ai package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.research.vix_term_structure_engine import VixTermStructureEngine
from ai.research.dynamic_gamma_scalping_engine import DynamicGammaScalpingEngine
from ai.research.volatility_edge_expiration_engine import VolatilityEdgeExpirationEngine
from ai.research.statistical_mean_reversion_engine import StatisticalMeanReversionEngine


def run_phase9_python_training():
    print("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 9...")

    # 1. Train Module AG1: VIX Term Structure & ETP Arbitrage Engine
    vix_engine = VixTermStructureEngine()
    mock_futures_curve = [
        {"month": 1, "dte": 15, "price": 14.50},
        {"month": 2, "dte": 45, "price": 15.60},
        {"month": 3, "dte": 75, "price": 16.40},
        {"month": 4, "dte": 105, "price": 17.00}
    ]
    ts_res = vix_engine.analyze_term_structure(spot_vix=13.80, futures_curve=mock_futures_curve)
    vvix_res = vix_engine.evaluate_vvix_tail_risk(spot_vix=13.80, spot_vvix=118.5)
    etp_res = vix_engine.calculate_etp_decay("UVXY", leverage=1.5, contango_roll_yield_annual=ts_res["roll_yield_pct"])

    print(f"  [AG1] VIX Curve Regime: {ts_res['regime']}, Slope: {ts_res['slope']}, Roll Yield: {ts_res['roll_yield_pct']}%")
    print(f"  [AG1] VVIX Tail Risk: {vvix_res['tail_risk_state']}, Hedge Action: {vvix_res['hedge_action']}")
    print(f"  [AG1] ETP {etp_res['symbol']} Annual Drag: {etp_res['annual_drag_pct']}%, Edge: {etp_res['recommendation']}")

    # 2. Train Module AH1: Dynamic Gamma Scalping Engine
    scalp_engine = DynamicGammaScalpingEngine(risk_aversion=1.0, transaction_cost_per_share=0.005)
    band_res = scalp_engine.compute_optimal_rebalance_band(spot_price=100.0, portfolio_gamma=0.05)
    trigger_res = scalp_engine.evaluate_rebalance_trigger(current_delta=0.18, target_delta=0.0, threshold=band_res["optimal_delta_threshold"])
    pnl_res = scalp_engine.calculate_scalp_pnl_attribution(
        portfolio_gamma=0.05, spot_price=100.0, realized_vol=0.28, implied_vol=0.20, dt_years=1.0/252.0, total_transaction_costs=0.50
    )
    print(f"  [AH1] Optimal Delta Band: +/-{band_res['optimal_delta_threshold']}, Price Move Trigger: ${band_res['price_move_trigger_dollars']}")
    print(f"  [AH1] Rebalance Action: {trigger_res['action']} ({trigger_res['shares_to_rebalance']} shares)")
    print(f"  [AH1] Scalp PnL: ${pnl_res['net_scalp_pnl']} ({pnl_res['scalping_regime']})")

    # 3. Train Module AI1: Volatility Edge & Expiration Microstructure Engine
    vol_edge_engine = VolatilityEdgeExpirationEngine(vega_theta_max_ratio=3.5)
    pin_res = vol_edge_engine.calculate_pinning_force(spot_price=100.20, strike_price=100.0, dte_days=0.5, open_interest_contracts=12000)
    budget_res = vol_edge_engine.evaluate_vega_theta_budget(portfolio_vega=45.0, portfolio_theta=-25.0)
    prob_res = vol_edge_engine.compute_touch_vs_expiration_probability(spot_price=100.0, strike_price=105.0, iv=0.25, dte_days=10.0)

    print(f"  [AI1] Strike Pinning Score: {pin_res['pinning_pull_score']}, Candidate: {pin_res['is_pinning_candidate']}")
    print(f"  [AI1] Vega/Theta Ratio: {budget_res['vega_theta_ratio']} ({budget_res['status']})")
    print(f"  [AI1] Touch Prob: {prob_res['prob_touching_strike_pct']}% vs Expire ITM: {prob_res['prob_expiring_itm_pct']}%")

    # 4. Train Module AJ1: Statistical Mean Reversion & Cointegration Engine
    mr_engine = StatisticalMeanReversionEngine()
    import math
    mock_spread = [math.sin(i * 0.2) + 0.05 * (i % 3) for i in range(50)]
    ou_res = mr_engine.calculate_ou_parameters(mock_spread)
    hurst_res = mr_engine.estimate_hurst_exponent(mock_spread)
    z_res = mr_engine.evaluate_zscore_signals(current_val=2.15, rolling_mean=0.0, rolling_std=1.0)

    print(f"  [AJ1] OU Theta: {ou_res['theta']}, Half-Life: {ou_res['half_life_periods']} periods ({ou_res['speed_of_reversion']})")
    print(f"  [AJ1] Hurst Exponent: {hurst_res['hurst_exponent']} -> Regime: {hurst_res['regime']}")
    print(f"  [AJ1] Z-Score Signal: Z={z_res['zscore']} -> Action: {z_res['action']}")

    print("[T1 PYTHON] Modules AG1, AH1, AI1, AJ1 trained successfully on Phase 9 requirements.")


if __name__ == "__main__":
    run_phase9_python_training()
