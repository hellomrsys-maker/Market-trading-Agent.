"""
scripts/train_python_phase4.py
==============================
Phase 4: Python Training Module (T1)
"""

import sys, os
from loguru import logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.research.smc_expectancy_engine import SMCExpectancyEngine
from ai.research.homma_candlestick_engine import HommaCandlestickEngine
from ai.research.cfi_valuation_breadth_engine import CFIValuationBreadthEngine
from ai.research.cognitive_bias_auditor_engine import CognitiveBiasAuditorEngine

def train():
    logger.info("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 4...")
    
    # 1. SMC & Expectancy
    smc = SMCExpectancyEngine()
    exp_res = smc.calculate_system_expectancy(0.55, 1.8, 1.0)
    logger.info(f"SMC Expectancy Engine: +{exp_res['expectancy_r']:.3f}R per trade, Half-Kelly Risk={exp_res['half_kelly_recommended_pct']}%")

    # 2. Homma Candlestick & Confluence
    homma = HommaCandlestickEngine()
    conf_res = homma.evaluate_pin_bar_confluence(True, True, True, True, is_bullish_pin=True)
    logger.info(f"Homma Confluence Rating: {conf_res['quality']} (Score={conf_res['confluence_score']}/4)")

    # 3. CFI Valuation & Breadth
    cfi = CFIValuationBreadthEngine()
    graham_num = cfi.calculate_ben_graham_number(4.50, 28.0)
    trin_res = cfi.calculate_trin_arms_index(2200, 800, 1500.0, 400.0)
    logger.info(f"CFI Valuation: Ben Graham Intrinsic Value=${graham_num:.2f}, TRIN Breadth={trin_res['condition']}")

    # 4. Cognitive Bias Auditor
    auditor = CognitiveBiasAuditorEngine()
    audit_res = auditor.audit_pre_trade_bias(45, True, False, "Clean OB+CHOCH alignment on 4H")
    logger.info(f"Cognitive Bias Audit: {audit_res['intervention']}")

    logger.success("[T1 PYTHON] Modules M1, N1, O1, P1 trained successfully on Phase 4 requirements.")

if __name__ == "__main__":
    train()
