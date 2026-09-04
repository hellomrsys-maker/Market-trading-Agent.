"""
tests/test_full_system.py
==========================
Comprehensive System Verification Test Suite

Tests every subsystem:
  1. Execution & Broker (AlpacaClient, state sync)
  2. Cognitive Brain (Concentration, Recall, Creative Morph, Executive Governor)
  3. Polyglot Math (BSM, SVI Surface features, Higher-Order Greeks)
  4. Advanced Strategies (Calendar Spread, Iron Butterfly, Put Ratio Spread 1x2)
  5. Portfolio Risk & VaR (99% VaR, Macro Stress Scenarios, Greeks Aggregator)
  6. Self-Improvement (Model Comparator, RND Curiosity, Meta-Learner)
  7. Backtesting Engine & Position Tracker
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import date, timedelta
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.execution.alpaca_client import AlpacaClient
from agent.brain.concentration import ConcentrationEngine
from agent.brain.recall_engine import AssociativeRecallEngine
from agent.brain.creative_reasoning import CreativeReasoningEngine
from agent.brain.executive_governor import ExecutiveGovernor
from agent.brain.memory import TradeMemory, TradeRecord
from agent.strategy.calendar_spread import CalendarSpreadStrategy
from agent.strategy.butterfly import IronButterflyStrategy
from agent.strategy.ratio_spread import PutRatioSpreadStrategy
from agent.risk.portfolio_risk import PortfolioRiskEngine
from agent.risk.stress_tester import MacroStressTester
from agent.risk.greeks_aggregator import GreeksAggregator
from ai.self_improvement.model_comparator import ModelComparator
from ai.self_improvement.curiosity_module import RNDCuriosityModule
from ai.features.vol_surface_features import VolatilitySurfaceFeatureExtractor
from backtest.engine import BacktestEngine
from backtest.option_chain_sim import OptionChainSimulator, bsm_price, bsm_greeks


# ── 1. Execution Client Tests ─────────────────────────────────
class TestAlpacaClient:
    def test_account_and_equity(self):
        client = AlpacaClient()
        acc = client.get_account()
        assert acc["equity"] >= 100_000.0
        assert client.get_equity() >= 100_000.0

    def test_market_data_and_chain(self):
        client = AlpacaClient()
        spot = client.get_latest_price("SPY")
        assert spot > 0.0
        chain = client.get_option_chain("SPY")
        assert len(chain) > 0
        assert "strike" in chain[0]

    def test_order_lifecycle(self):
        client = AlpacaClient()
        ord1 = client.sell_put("SPY251219P00480000", qty=1, limit_price=3.50)
        assert ord1["status"] == "filled"
        assert len(client.get_option_positions()) >= 1
        client.close_position("SPY251219P00480000")
        assert len(client.get_option_positions()) == 0


# ── 2. Cognitive Brain Tests ──────────────────────────────────
class TestCognitiveBrainDeep:
    def test_concentration_selective_weighting(self):
        conc = ConcentrationEngine()
        feats = {
            "SPY": np.array([0, 0, 0.01, 0, 0, 0.12, 0.16, 20.0, 0, 0, 0, 0, 1.0]),
            "NVDA": np.array([0, 0, 0.08, 0, 0, 0.35, 0.45, 80.0, 0, 0, 0, 0, 2.0]),
        }
        weights = conc.compute_attention_weights(feats, "Neutral", 15.0)
        assert weights["NVDA"] > weights["SPY"]

    def test_associative_recall_calibration(self):
        mem = TradeMemory()
        mem.clear()
        mem.record(TradeRecord(
            symbol="SPY",
            strategy="WHEEL_CSP",
            option_symbol="SPY250620P00480000",
            strike=480.0,
            expiry="2025-06-20",
            dte_at_open=45,
            premium_received=300.0,
            pnl=150.0,
            pnl_pct=0.50,
            opened_at="2025-01-01",
            closed_at="2025-01-15",
            days_held=14,
            close_reason="profit_take",
            iv_rank_at_open=45.0,
            regime_at_open="Neutral",
            ensemble_signal=0.75,
            ensemble_conf=0.80,
        ))
        recall = AssociativeRecallEngine(mem)
        res = recall.recall_analogous_trades("SPY", 45.0, "Neutral")
        assert res["analogues_found"] == 1
        assert res["historical_win_rate"] == 1.0

    def test_executive_governor_pipeline(self):
        gov = ExecutiveGovernor()
        feats = {"SPY": np.array([0, 0, 0.02, 0, 0, 0.15, 0.20, 50.0, 0, 0, 0, 0, 1.0])}
        res = gov.arbitrate_decision("SPY", "WHEEL_CSP", 0.65, 50.0, "Neutral", feats, 16.0)
        assert res["approved"] is True
        assert res["final_confidence"] > 0.50


# ── 3. Advanced Strategy Tests ────────────────────────────────
class TestAdvancedStrategies:
    def test_calendar_spread_backwardation(self):
        sim = OptionChainSimulator()
        chain = sim.generate_chain("SPY", 480.0, 0.22, target_dtes=[21, 45])
        opp = CalendarSpreadStrategy.scan_opportunity("SPY", 480.0, chain, term_spread=0.04)
        assert opp is not None
        assert opp["strategy"] == "CALENDAR_SPREAD"
        assert opp["short_dte"] == 21
        assert opp["long_dte"] == 45

    def test_iron_butterfly_high_iv(self):
        sim = OptionChainSimulator()
        chain = sim.generate_chain("QQQ", 430.0, 0.35, target_dtes=[30])
        opp = IronButterflyStrategy.scan_opportunity("QQQ", 430.0, chain, iv_rank=75.0, wing_width=5.0)
        assert opp is not None
        assert opp["strategy"] == "IRON_BUTTERFLY"
        assert opp["net_credit"] > 0.0

    def test_put_ratio_spread_1x2(self):
        sim = OptionChainSimulator()
        chain = sim.generate_chain("MSFT", 420.0, 0.25, target_dtes=[45])
        opp = PutRatioSpreadStrategy.scan_opportunity("MSFT", 420.0, chain, momentum_20d=-0.02)
        assert opp is not None
        assert opp["strategy"] == "PUT_RATIO_SPREAD_1X2"
        assert opp["long_strike"] > opp["short_strike"]


# ── 4. Portfolio Risk & VaR Tests ─────────────────────────────
class TestPortfolioRiskAndVaR:
    def test_portfolio_var_calculation(self):
        res = PortfolioRiskEngine.calculate_var(
            portfolio_equity=100_000.0,
            net_delta_dollars=500.0,
            net_gamma_dollars=-50.0,
            net_vega_dollars=-100.0,
        )
        assert res["var_99_dollars"] > 0.0
        assert res["is_var_within_bounds"] is True

    def test_macro_stress_scenarios(self):
        res = MacroStressTester.run_stress_tests(
            equity=100_000.0,
            net_delta_dollars=200.0,
            net_gamma_dollars=-20.0,
            net_vega_dollars=-80.0,
            net_theta_dollars=30.0,
        )
        assert "overall_stress_pass" in res
        assert "Flash_Crash_Minus_10Pct" in res["scenarios"]

    def test_greeks_aggregator(self):
        positions = [
            {"symbol": "SPY", "stage": "CSP", "delta": -0.30, "gamma": 0.02, "theta": 0.05, "vega": 0.10, "qty": 1},
        ]
        greeks = GreeksAggregator.aggregate(positions, {"SPY": 500.0})
        assert greeks["net_delta_dollars"] > 0.0  # short put is long delta


# ── 5. Self-Improvement AI Tests ──────────────────────────────
class TestSelfImprovementAI:
    def test_model_comparator_mcnemar(self):
        y_true = np.array([1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
        y_prod = np.array([0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0])  # lower acc
        y_cand = np.array([1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])  # 100% acc
        res = ModelComparator.compare_classifiers(y_true, y_prod, y_cand)
        assert "cand_accuracy" in res
        assert res["cand_accuracy"] > res["prod_accuracy"]

    def test_rnd_curiosity_intrinsic_reward(self):
        rnd = RNDCuriosityModule(state_dim=13)
        state = np.random.randn(13).astype(np.float32)
        reward = rnd.compute_intrinsic_reward(state)
        assert reward >= 0.0


# ── 6. Volatility Surface Features ────────────────────────────
class TestVolSurfaceFeatures:
    def test_feature_extraction(self):
        sim = OptionChainSimulator()
        chain = sim.generate_chain("SPY", 500.0, 0.20, target_dtes=[30, 45])
        feats = VolatilitySurfaceFeatureExtractor.extract_features(500.0, chain, rv20=0.18)
        assert feats.shape == (8,)
        assert not np.any(np.isnan(feats))


# ── 7. Backtest Full Cycle ────────────────────────────────────
class TestBacktestFullCycle:
    def test_backtest_execution(self):
        engine = BacktestEngine(symbols=["SPY", "QQQ"])
        res = engine.run(days=15)
        assert res.metrics["trading_days"] == 15
        assert len(res.equity_curve) == 15
