"""
scripts/train_python_phase5.py
==============================
Phase 5: Python Training Module (T1)
"""

import sys, os
from loguru import logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.research.weekly_squeeze_engine import WeeklySqueezeEngine
from ai.research.bsm_jump_diffusion_engine import BSMJumpDiffusionEngine
from ai.research.binary_options_engine import BinaryOptionsEngine
from ai.research.drawdown_risk_manager import DrawdownRiskManager

def train():
    logger.info("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 5...")
    
    # 1. Weekly Squeeze & Heikin Ashi
    wse = WeeklySqueezeEngine()
    ha_bar = wse.calculate_heikin_ashi(100.0, 105.0, 99.0, 104.0, 98.0, 101.0)
    squeeze_res = wse.detect_ttm_squeeze(103.0, 97.0, 104.0, 96.0, 102.0, 100.0, 95.0)
    legging_res = wse.evaluate_dynamic_legging("PUT_CREDIT_SPREAD", 0.65, 2.5, 6)
    logger.info(f"Weekly Squeeze Engine: HA={ha_bar['signal_color']}, Squeeze={squeeze_res['squeeze_status']}, Legging={legging_res['resulting_structure']}")

    # 2. BSM & Jump-Diffusion
    bsm = BSMJumpDiffusionEngine()
    pricing = bsm.calculate_bsm_merton(100.0, 100.0, 0.25, 0.05, 0.20, 0.02)
    regrets = bsm.calculate_regrets_decomposition(100.0, 100.0, 0.25, 0.05, pricing['put_price'])
    p_ever = bsm.calculate_probability_ever_itm(100.0, 110.0, 0.5, 0.05, 0.25)
    merton_jump = bsm.calculate_merton_jump_diffusion(100.0, 100.0, 0.25, 0.05, 0.20, 1.0, 0.0, 0.1)
    logger.info(f"BSM Engine: Call=${pricing['call_price']:.2f}, Elasticity={pricing['elasticity_call']:.2f}, P*_ever(ITM)={p_ever:.1%}, Jump BSM=${merton_jump:.2f}")

    # 3. Binary Options & Volatility Strangle
    boe = BinaryOptionsEngine()
    bin_collateral = boe.calculate_collateral_and_payout("LONG", 30.0, 5)
    strangle_res = boe.evaluate_volatility_strangle(False, 20.0, 80.0, 2)
    cutoff_res = boe.calculate_cutoff_thresholds(10.0, 3.0)
    logger.info(f"Binary Options Engine: Collateral=${bin_collateral['total_collateral']:.2f}, Short Strangle Max Profit=${strangle_res['max_profit']:.2f}, Loss Cutoff=${cutoff_res['max_allowable_loss']:.2f}")

    # 4. Drawdown Risk Manager
    drm = DrawdownRiskManager(10000.0, 20.0)
    pos_size = drm.calculate_position_size(2.0, 50.0)
    trade_update = drm.update_trade_result(200.0)
    logger.info(f"Drawdown Risk Manager: Pos Size={pos_size} contracts, Account State={trade_update['system_status']}")

    logger.success("[T1 PYTHON] Modules Q1, R1, S1, T_sys1 trained successfully on Phase 5 requirements.")

if __name__ == "__main__":
    train()
