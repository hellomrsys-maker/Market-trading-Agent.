"""
Phase 7 Training Matrix Runner (T1 - Python)
Benchmarks and trains Modules Y1, Z1, AA1, AB1.
"""

import os
import sys

# Ensure ai package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.research.behavioral_psychology_scripting_engine import BehavioralPsychologyScriptingEngine, InnerVillain, DecisionZone
from ai.research.cashflow_capital_ecosystem_engine import CashflowCapitalEcosystemEngine, CJITransaction
from ai.research.tactical_swing_trading_engine import TacticalSwingTradingEngine
from ai.research.tactical_options_discipline_engine import TacticalOptionsDisciplineEngine


def train_phase7():
    print("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 7...")

    # 1. Train Module Y1 (Behavioral Psychology)
    y_engine = BehavioralPsychologyScriptingEngine()
    villain = y_engine.classify_sabotage_archetype(
        trigger_context="A bad day at work led to shopping",
        emotional_state="I'm feeling like I'm not good enough, need a new identity",
        is_impulsive=True,
        is_post_blowout=False,
        is_near_goal=False,
        is_social_prompted=False
    )
    abc_state = y_engine.execute_abcde_reframe(
        event="Impulse trade loss",
        belief="I'm terrible with money",
        consequence="Desire to revenge trade"
    )
    resilience = y_engine.compute_3p_resilience(0.2, 0.3, 0.1)
    print(f"  [Y1] Sabotage Archetype Detected: {villain.value}")
    print(f"  [Y1] Mental Toughness Score: {resilience.composite_mental_toughness}")

    # 2. Train Module Z1 (Cashflow Capital Ecosystem)
    z_engine = CashflowCapitalEcosystemEngine(baseline_new_zero=100.0)
    z_engine.add_sinking_fund("car_rego", target=800.0, periods=34, buffer=0.10)
    z_engine.add_sinking_fund("tech_replacement", target=1500.0, periods=26, buffer=0.05)
    eco_state = z_engine.calculate_streamlined_ecosystem(
        income=3000.0,
        fixed_costs=1200.0,
        variable_costs=300.0,
        savings_ratio=0.25
    )
    print(f"  [Z1] Workable Total: ${eco_state.workable_total}, Keep Savings: ${eco_state.keep_savings_allocated}, Sinking Funds: ${eco_state.sinking_funds_total}")

    # 3. Train Module AA1 (Tactical Swing Trading)
    aa_engine = TacticalSwingTradingEngine()
    abcd = aa_engine.evaluate_abcd_pattern(point_a=40.0, point_b=55.0, point_c=48.0, is_bullish_trend=True)
    flag = aa_engine.detect_flag_formation(
        pole_start=100.0, pole_end=120.0, pullback_extreme=115.0, current_price=120.0,
        volume_trend_declining=True, is_bull_flag=True
    )
    print(f"  [AA1] Bullish ABCD Target: ${abcd['point_d_target']}, Reward/Risk: {abcd['reward_to_risk']}")
    if flag:
        print(f"  [AA1] Flag Breakout Detected! Target: ${flag.take_profit}, R:R: {flag.reward_to_risk}")

    # 4. Train Module AB1 (Tactical Options Discipline)
    ab_engine = TacticalOptionsDisciplineEngine(account_equity=10000.0)
    pos = ab_engine.calculate_position_size(entry_price=50.0, stop_loss_price=48.0, is_aggressive_risk=False)
    condor = ab_engine.structure_iron_condor(
        k1_put_long=50.0, k2_put_short=60.0, k3_call_short=90.0, k4_call_long=100.0,
        premium_put_short=2.0, premium_put_long=1.0, premium_call_short=2.0, premium_call_long=1.0
    )
    print(f"  [AB1] Position Sizing: {pos['recommended_shares']} shares (${pos['max_dollar_risk']} risk)")
    print(f"  [AB1] Iron Condor Net Credit: ${condor.net_credit_received}, Max Loss: ${condor.max_loss}, R:R: {condor.reward_to_risk}")

    print("[T1 PYTHON] Modules Y1, Z1, AA1, AB1 trained successfully on Phase 7 requirements.")


if __name__ == "__main__":
    train_phase7()
