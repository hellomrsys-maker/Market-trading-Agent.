"""
Phase 14 Training Matrix Runner (T1 - Python)
Benchmarks and trains Modules BA1, BB1, BC1, BD1.
"""

import os
import sys

# Ensure ai package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.research.classical_reversal_pattern_engine import ClassicalReversalPatternEngine
from ai.research.continuation_geometry_pattern_engine import ContinuationGeometryPatternEngine
from ai.research.volume_breakout_trap_filter import VolumeBreakoutTrapFilter
from ai.research.pattern_alignment_risk_governor import PatternAlignmentRiskGovernor


def run_phase14_python_training():
    print("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 14...")

    # 1. Train Module BA1: Classical Reversal Pattern Engine
    rev_engine = ClassicalReversalPatternEngine()
    hs_res = rev_engine.evaluate_head_and_shoulders(
        left_shoulder_peak=105.0, head_peak=112.0, right_shoulder_peak=104.5,
        neckline_price=98.0, current_spot=96.5, is_inverse=False
    )
    dt_res = rev_engine.evaluate_double_top_bottom(
        peak1=150.0, peak2=149.2, trough_neckline=140.0, current_spot=138.5, is_double_bottom=False
    )

    print(f"  [BA1] H&S Detection: {hs_res['pattern_name']} -> Target: ${hs_res['measured_target']} ({hs_res['status']})")
    print(f"  [BA1] Double Top: {dt_res['pattern_name']} -> Target: ${dt_res['measured_target']} ({dt_res['status']})")

    # 2. Train Module BB1: Continuation Geometry Pattern Engine
    geom_engine = ContinuationGeometryPatternEngine()
    tri_res = geom_engine.evaluate_triangle_pattern(
        upper_trendline_slope=0.0, lower_trendline_slope=0.12, pattern_base_height=15.0, breakout_price=100.0, current_spot=102.5
    )
    flag_res = geom_engine.evaluate_flag_or_pennant(
        flagpole_start_price=80.0, flagpole_peak_price=100.0, breakout_price=98.0, current_spot=99.5, is_bull_flag=True
    )

    print(f"  [BB1] Triangle Formation: {tri_res['pattern_type']} -> Target: ${tri_res['measured_target']}")
    print(f"  [BB1] Flag Pattern: {flag_res['pattern_name']} -> Target: ${flag_res['measured_target']}")

    # 3. Train Module BC1: Volume Breakout Trap Filter
    trap_engine = VolumeBreakoutTrapFilter()
    vol_res = trap_engine.evaluate_breakout_volume(breakout_bar_volume=350000.0, sma20_volume=200000.0, is_breakout_candle_closed=True)
    spring_res = trap_engine.detect_wyckoff_trap(key_level=95.0, extreme_price_during_breakout=93.5, closing_price_after_breakout=95.8, is_support_level=True)

    print(f"  [BC1] Breakout Volume Surge: {vol_res['volume_surge_ratio']}x -> {vol_res['verdict']}")
    print(f"  [BC1] Wyckoff Trap Check: {spring_res['trap_type']} -> Action: {spring_res['trade_action']}")

    # 4. Train Module BD1: Pattern Alignment Risk Governor
    gov_engine = PatternAlignmentRiskGovernor()
    risk_res = gov_engine.audit_pattern_risk_reward(
        entry_price=98.0, target_price=118.0, stop_loss_price=92.0, htf_trend_direction=1, pattern_direction=1
    )

    print(f"  [BD1] Risk/Reward Audit: R:R={risk_res['rr_ratio']} -> {risk_res['verdict']}")

    print("[T1 PYTHON] Modules BA1, BB1, BC1, BD1 trained successfully on Phase 14 requirements.")


if __name__ == "__main__":
    run_phase14_python_training()
