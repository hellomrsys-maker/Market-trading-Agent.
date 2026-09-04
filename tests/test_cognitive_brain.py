"""
tests/test_cognitive_brain.py
==============================
Unit tests for the cognitive brain architecture:
  - ConcentrationEngine (Attention weighting & noise suppression)
  - AssociativeRecallEngine (Episodic retrieval & probability calibration)
  - CreativeReasoningEngine (Lateral defense & asymmetric wings)
  - ExecutiveGovernor (Arbitration pipeline)
"""

from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.brain.concentration import ConcentrationEngine
from agent.brain.recall_engine import AssociativeRecallEngine
from agent.brain.creative_reasoning import CreativeReasoningEngine
from agent.brain.executive_governor import ExecutiveGovernor
from agent.brain.memory import TradeMemory


class TestConcentrationEngine:
    def test_attention_weights_sum_to_one(self):
        engine = ConcentrationEngine()
        feats = {
            "SPY": np.array([0, 0, 0.02, 0, 0, 0.15, 0.20, 45.0, 0, 0, 0, 0, 1.0]),
            "QQQ": np.array([0, 0, -0.01, 0, 0, 0.18, 0.22, 55.0, 0, 0, 0, 0, 1.2]),
            "NVDA": np.array([0, 0, 0.05, 0, 0, 0.35, 0.40, 75.0, 0, 0, 0, 0, 1.5]),
        }
        weights = engine.compute_attention_weights(feats, "Neutral", 16.0)
        assert len(weights) == 3
        assert sum(weights.values()) == pytest.approx(1.0, abs=1e-3)
        # NVDA has highest IV rank and momentum -> should get highest attention
        assert weights["NVDA"] > weights["SPY"]


class TestCreativeReasoningEngine:
    def test_threatened_csp_morph(self):
        engine = CreativeReasoningEngine()
        pos = {"strategy": "WHEEL_CSP", "symbol": "NVDA", "strike": 120.0}
        morph = engine.synthesize_defensive_morph(pos, current_spot=118.0, current_iv=0.45)
        assert morph is not None
        assert morph["action"] == "MORPH_ROLL_OUT_AND_DOWN"
        assert morph["target_strike"] < 120.0

    def test_asymmetric_wings_skew(self):
        engine = CreativeReasoningEngine()
        # High put skew -> put wing narrowed, call wing widened
        put_wing, call_wing = engine.engineer_asymmetric_condor_wings(spot=480.0, put_skew=0.06, base_wing=5.0)
        assert put_wing < 5.0
        assert call_wing > 5.0


class TestExecutiveGovernor:
    def test_decision_arbitration(self):
        gov = ExecutiveGovernor()
        feats = {"SPY": np.array([0, 0, 0.01, 0, 0, 0.15, 0.20, 50.0, 0, 0, 0, 0, 1.0])}
        dec = gov.arbitrate_decision(
            symbol="SPY",
            base_strategy="WHEEL_CSP",
            base_confidence=0.60,
            iv_rank=50.0,
            macro_regime="Neutral",
            universe_features=feats,
            current_vix=16.0,
        )
        assert "approved" in dec
        assert "final_confidence" in dec
        assert dec["approved"] is True
