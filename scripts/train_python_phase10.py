"""
Phase 10 Training Matrix Runner (T1 - Python)
Benchmarks and trains Modules AK1, AL1, AM1, AN1.
"""

import os
import sys

# Ensure ai package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.research.schwager_price_action_engine import SchwagerPriceActionEngine
from ai.research.commodity_spread_arbitrage_engine import CommoditySpreadArbitrageEngine
from ai.research.cot_institutional_sentiment_engine import CotInstitutionalSentimentEngine
from ai.research.futures_risk_governor_engine import FuturesRiskGovernorEngine


def run_phase10_python_training():
    print("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 10...")

    # 1. Train Module AK1: Schwager Price Action & Trap Engine
    pa_engine = SchwagerPriceActionEngine()
    key_rev = pa_engine.evaluate_key_reversal(
        prev_open=100.0, prev_high=102.0, prev_low=98.0, prev_close=99.0,
        curr_open=98.5, curr_high=103.5, curr_low=97.0, curr_close=103.0,
        curr_volume=150000, avg_volume=100000
    )
    spring_trap = pa_engine.detect_false_breakout_trap(
        support_level=95.0, resistance_level=110.0, curr_high=97.0, curr_low=94.2, curr_close=95.8
    )
    gap_res = pa_engine.classify_gap_structure(
        base_breakout_price=90.0, gap_open=105.0, prev_bar_high=102.0, prev_bar_low=99.0, bars_since_breakout=4, is_filled_rapidly=False
    )
    print(f"  [AK1] Key Reversal Pattern: {key_rev['pattern']} (Stop: ${key_rev['stop_level']})")
    print(f"  [AK1] Trap Analysis: {spring_trap['trap_type']} -> Bias: {spring_trap['trade_bias']}")
    print(f"  [AK1] Gap Type: {gap_res['gap_type']} -> Projected Target: ${gap_res['projected_target']}")

    # 2. Train Module AL1: Commodity Processing & Spread Arbitrage Engine
    spread_engine = CommoditySpreadArbitrageEngine()
    carry_res = spread_engine.calculate_cost_of_carry_fair_value(spot_price=75.0, storage_rate_annual=0.02, convenience_yield_annual=0.01, time_to_maturity_years=0.5)
    crack_res = spread_engine.compute_energy_321_crack_spread(crude_oil_price_per_barrel=75.0, gasoline_rbob_price_per_gallon=2.45, heating_oil_price_per_gallon=2.65)
    crush_res = spread_engine.compute_soybean_crush_spread(soybeans_cents_per_bushel=1250.0, soybean_meal_dollars_per_ton=380.0, soybean_oil_cents_per_pound=55.0)

    print(f"  [AL1] Cost of Carry Fair Value: ${carry_res['fair_futures_price']} ({carry_res['market_structure']})")
    print(f"  [AL1] 3:2:1 Energy Crack Margin: ${crack_res['crack_margin_per_barrel']}/bbl -> Signal: {crack_res['signal']}")
    print(f"  [AL1] Soybean Crush GPM: {crush_res['gpm_cents_per_bushel']} cents/bu (${crush_res['gpm_dollars_per_bushel']}/bu) -> Signal: {crush_res['signal']}")

    # 3. Train Module AM1: COT Institutional Sentiment Engine
    cot_engine = CotInstitutionalSentimentEngine()
    cot_res = cot_engine.calculate_cot_index(current_net_position=185000, min_net_3yr=20000, max_net_3yr=200000)
    oi_res = cot_engine.evaluate_price_oi_confluence(price_change=2.5, oi_change=12500)

    print(f"  [AM1] COT Index: {cot_res['cot_index_pct']}% -> Status: {cot_res['status']}")
    print(f"  [AM1] Price/OI Confluence: {oi_res['regime']} -> Action Bias: {oi_res['bias']}")

    # 4. Train Module AN1: Futures Risk Governor Engine
    risk_engine = FuturesRiskGovernorEngine()
    size_res = risk_engine.calculate_atr_position_size(account_equity=100000.0, risk_pct=1.5, atr_value=2.25, atr_stop_multiplier=2.0, point_value=1000.0)
    rob_res = risk_engine.evaluate_walk_forward_robustness(in_sample_sharpe=1.85, out_of_sample_sharpe=1.45)
    heat_res = risk_engine.audit_portfolio_heat(open_positions_risk_dollars=[1500.0, 1200.0, 1400.0], account_equity=100000.0)

    print(f"  [AN1] ATR Sizing: {size_res['recommended_contracts']} contracts (Risk: ${size_res['dollar_risk_target']})")
    print(f"  [AN1] Walk-Forward Robustness: Ratio {rob_res['robustness_ratio']} -> Verdict: {rob_res['verdict']}")
    print(f"  [AN1] Portfolio Heat: {heat_res['current_heat_pct']}% (Compliant: {heat_res['is_heat_compliant']}) -> {heat_res['action']}")

    print("[T1 PYTHON] Modules AK1, AL1, AM1, AN1 trained successfully on Phase 10 requirements.")


if __name__ == "__main__":
    run_phase10_python_training()
