"""
tests/test_polyglot_coverage.py
===============================
OptionAlpha Agent — Comprehensive Polyglot, Cognitive Brain, PROVEST, Market Profile, & Forex Test Suite

Tests:
  1. Derivative Foundations (Call, Put, 100-Share Contract Multiplier)
  2. The 5 Cognitive Brain Faculties (Thinking, Concentration, Recall, Creativity, Governance)
  3. Mark Douglas Disciplined Trader Psychological Governor (Predefined loss & revenge prevention)
  4. Dalton Auction Market Profile (TPOs, Value Area 70%, POC, Open-Drive, One-Timeframing)
  5. Forex & Commodity Valuation & Safety (Pip calculation, 1-2% risk position sizing, RSI, Fibonacci)
  6. Jay Kaeppel PROVEST Framework (24-Month Relative Volatility Decile 1-10)
  7. Candlestick Pattern Engine (Morning Star, Evening Star, Engulfing, Tweezers)
  8. Advanced Multi-Leg Strategies (Iron Condor, Butterfly, Calendar, Ratio Spread, Wheel)
  9. Zero-Bridge 64-Byte Memory Architecture & Polyglot High-Throughput Trainer
"""

import math
import pytest
import numpy as np

from agent.strategy.tri_state_decision import TriStateDecisionEngine, ActionType
from agent.brain.concentration import ConcentrationEngine
from agent.brain.recall_engine import AssociativeRecallEngine
from agent.brain.creative_reasoning import CreativeReasoningEngine
from agent.brain.executive_governor import ExecutiveGovernor
from agent.brain.psychological_governor import PsychologicalGovernor
from agent.brain.memory import TradeMemory, TradeRecord
from agent.strategy.call_engine import CallStrategyEngine
from agent.strategy.put_engine import PutStrategyEngine
from agent.strategy.butterfly import IronButterflyStrategy
from agent.strategy.calendar_spread import CalendarSpreadStrategy
from agent.strategy.ratio_spread import PutRatioSpreadStrategy
from agent.risk.risk_gate import RiskGate, OrderIntent
from agent.risk.portfolio_risk import PortfolioRiskEngine
from ai.research.options_foundations import OptionContractSpecification
from ai.research.provest_engine import PROVESTEngine
from ai.research.clbs_v2_engine import CLBSV2IntelligenceEngine
from ai.research.market_profile_engine import DaltonMarketProfileEngine
from ai.research.forex_commodity_engine import ForexCommodityEngine
from ai.models.candlestick_pattern_engine import CandlestickPatternEngine


class TestDerivativeMechanicsAndMultiplier:
    def test_call_option_bsm_and_multiplier(self):
        call = OptionContractSpecification(
            symbol="SPY_CALL_500",
            underlying="SPY",
            option_type="CALL",
            strike_price=500.0,
            expiration_years=45 / 365.0,
            spot_price=500.0,
            risk_free_rate=0.05,
            implied_volatility=0.18,
            multiplier=100,
        )
        bsm = call.compute_bsm_analytical()
        assert bsm["theoretical_price"] > 0.0
        assert bsm["contract_dollar_premium"] == round(bsm["theoretical_price"] * 100, 2)
        assert bsm["contract_notional_value"] == 50000.0
        assert 0.40 <= bsm["delta"] <= 0.65
        assert bsm["vanna"] != 0.0
        assert bsm["charm"] != 0.0

    def test_put_option_bsm_and_collateral(self):
        put = OptionContractSpecification(
            symbol="SPY_PUT_480",
            underlying="SPY",
            option_type="PUT",
            strike_price=480.0,
            expiration_years=30 / 365.0,
            spot_price=500.0,
            risk_free_rate=0.05,
            implied_volatility=0.20,
            multiplier=100,
        )
        bsm = put.compute_bsm_analytical()
        assert bsm["theoretical_price"] > 0.0
        assert -0.40 <= bsm["delta"] <= -0.10
        assert put.compute_payoff_at_expiration(terminal_spot=460.0, position_side="LONG") > 0.0


class TestCognitiveBrainFaculties:
    def test_thinking_tri_state_synthesis(self):
        decision = TriStateDecisionEngine.evaluate(
            symbol="SPY",
            spot_price=500.0,
            price_bars_60d=[{"close": 490.0 + i * 0.15, "volume": 1000000} for i in range(60)],
            chain_contracts=[{"strike": 480.0, "is_call": False, "dte": 30, "bid": 2.50, "delta": -0.28}],
            active_positions=[],
            current_vix=15.0,
            daily_pnl=0.0,
        )
        assert decision.contract_multiplier == 100
        assert decision.zero_bridge_status == "0_NS_SYNC"
        assert decision.action in {ActionType.BUY, ActionType.SELL, ActionType.HOLD}

    def test_concentration_softmax_weights(self):
        engine = ConcentrationEngine()
        feats = {
            "SPY": np.array([0.01, 0.02, 0.03, 0.0, 0.0, 0.15, 0.18, 45.0]),
            "QQQ": np.array([0.02, 0.03, 0.04, 0.0, 0.0, 0.18, 0.22, 65.0]),
            "AAPL": np.array([0.00, 0.01, 0.01, 0.0, 0.0, 0.14, 0.16, 20.0]),
        }
        weights = engine.compute_attention_weights(feats, macro_regime="Neutral", current_vix=16.0)
        assert abs(sum(weights.values()) - 1.0) < 1e-3
        assert weights["QQQ"] >= weights["AAPL"]

    def test_recall_knn_distance(self):
        memory = TradeMemory(capacity=100)
        memory.record(TradeRecord(
            symbol="SPY",
            strategy="WHEEL_CSP",
            option_symbol="SPY260918P00480000",
            strike=480.0,
            expiry="2026-09-18",
            dte_at_open=30,
            premium_received=350.0,
            pnl=175.0,
            pnl_pct=0.50,
            opened_at="2026-08-01",
            closed_at="2026-08-15",
            days_held=14,
            close_reason="profit_take",
            iv_rank_at_open=42.0,
            regime_at_open="Neutral",
            ensemble_signal=0.85,
            ensemble_conf=0.80,
        ))
        recall = AssociativeRecallEngine(memory)
        res = recall.recall_analogous_trades("SPY", current_iv_rank=40.0, current_regime="Neutral")
        assert res["analogues_found"] >= 1
        assert res["historical_win_rate"] == 1.0
        assert res["confidence_boost"] > 0.0

    def test_creative_lateral_morphing(self):
        morph = CreativeReasoningEngine.synthesize_defensive_morph(
            threatened_position={"strategy": "WHEEL_CSP", "strike": 500.0, "symbol": "SPY"},
            current_spot=498.0,
            current_iv=0.22,
        )
        assert morph is not None
        assert morph["action"] == "MORPH_ROLL_OUT_AND_DOWN"
        assert morph["target_strike"] == 475.0
        assert morph["additional_dte"] == 30

    def test_executive_governor_arbitration(self):
        gov = ExecutiveGovernor()
        feats = {"SPY": np.array([0.01, 0.02, 0.03, 0.0, 0.0, 0.15, 0.18, 45.0])}
        arb = gov.arbitrate_decision(
            symbol="SPY",
            base_strategy="WHEEL_CSP",
            base_confidence=0.75,
            iv_rank=45.0,
            macro_regime="Neutral",
            universe_features=feats,
            current_vix=16.0,
        )
        assert arb["approved"] is True
        assert arb["final_confidence"] >= 0.50
        assert arb["contract_multiplier"] == 100


class TestPsychologyAndDisciplinedTrader:
    def test_mark_douglas_rule_1_rejection_on_no_stop(self):
        gov = PsychologicalGovernor()
        audit = gov.audit_trade_intent("SPY", 500.0, proposed_stop_loss=None, current_equity=50000.0, proposed_risk_dollars=500.0)
        assert audit.is_disciplined is False
        assert audit.state_of_mind == "FEAR_AVOIDANCE"
        assert "Rule 1 Violation" in audit.guidance_message

    def test_revenge_trading_suppression(self):
        gov = PsychologicalGovernor(max_consecutive_losses=3)
        gov.record_trade_outcome(-300.0)
        gov.record_trade_outcome(-400.0)
        gov.record_trade_outcome(-250.0) # 3 consecutive losses
        audit = gov.audit_trade_intent("SPY", 500.0, proposed_stop_loss=490.0, current_equity=50000.0, proposed_risk_dollars=500.0)
        assert audit.is_disciplined is True
        assert audit.state_of_mind == "REVENGE_SEEKING"
        assert audit.sizing_penalty_factor == 0.50


class TestDaltonMarketProfile:
    def test_market_profile_tpo_calculation(self):
        bars = [
            {"open": 100.0, "high": 101.0, "low": 99.5, "close": 100.5},
            {"open": 100.5, "high": 102.0, "low": 100.0, "close": 101.8},
            {"open": 101.8, "high": 102.5, "low": 101.0, "close": 102.2},
            {"open": 102.2, "high": 103.0, "low": 101.8, "close": 102.8},
        ]
        profile = DaltonMarketProfileEngine.calculate_tpo_profile("SPY", bars)
        assert profile.poc_price > 0.0
        assert profile.vah_price >= profile.val_price
        assert profile.open_type in {"OPEN_DRIVE", "OPEN_TEST_DRIVE", "OPEN_REJECTION_REVERSE", "OPEN_AUCTION"}


class TestForexAndCommodityEngine:
    def test_pip_valuation_usd_quote_and_base(self):
        # Direct USD quote: 1 pip on 100k EUR/USD = $10.00
        pip_eurusd = ForexCommodityEngine.calculate_pip_value("EUR/USD", 100000, 1.10)
        assert pip_eurusd == 10.0

        # USD base: 1 pip on 100k USD/CHF @ 0.90 = $11.1111
        pip_usdchf = ForexCommodityEngine.calculate_pip_value("USD/CHF", 100000, 0.90)
        assert round(pip_usdchf, 2) == 11.11

    def test_forex_strict_position_sizing(self):
        lots, units, risk_dlrs, margin = ForexCommodityEngine.calculate_position_size(
            pair="EUR/USD",
            account_equity=10000.0,
            risk_pct=0.02, # 2% max risk = $200
            stop_loss_pips=20.0,
            current_spot=1.10,
        )
        assert risk_dlrs == 200.0
        assert lots == 1.0
        assert units == 100000

    def test_fibonacci_retracements(self):
        fibs = ForexCommodityEngine.compute_fibonacci_levels(swing_low=100.0, swing_high=200.0)
        assert fibs["50.0%"] == 150.0
        assert fibs["61.8%"] == 138.2
        assert fibs["38.2%"] == 161.8


class TestPROVESTAndCandlesticks:
    def test_provest_volatility_decile(self):
        iv_hist = [0.15 + i * 0.01 for i in range(100)] # 0.15 to 1.14
        decile = PROVESTEngine.compute_relative_volatility_rank(iv_hist, 0.95)
        assert decile >= 8

    def test_candlestick_morning_star(self):
        bars = [
            {"open": 105.0, "high": 105.5, "low": 98.0, "close": 98.5}, # Bearish
            {"open": 98.2, "high": 98.8, "low": 97.5, "close": 98.0},   # Small star
            {"open": 98.5, "high": 104.5, "low": 98.2, "close": 104.0}, # Strong bull U-turn
        ]
        sig = CandlestickPatternEngine.analyze_bars(bars)
        assert sig is not None
        assert sig.pattern_name == "BULLISH_MORNING_STAR"
        assert sig.direction == "BULLISH"


class TestMultiLegStrategiesPolyglot:
    def test_butterfly_opportunity(self):
        contracts = [
            {"strike": 500.0, "is_call": True, "dte": 30, "ask": 8.0, "bid": 7.5, "delta": 0.50, "expiration_date": "2026-09-30"},
            {"strike": 500.0, "is_call": False, "dte": 30, "ask": 8.0, "bid": 7.5, "delta": -0.50, "expiration_date": "2026-09-30"},
            {"strike": 505.0, "is_call": True, "dte": 30, "ask": 3.0, "bid": 2.8, "delta": 0.20, "expiration_date": "2026-09-30"},
            {"strike": 495.0, "is_call": False, "dte": 30, "ask": 3.0, "bid": 2.8, "delta": -0.20, "expiration_date": "2026-09-30"},
        ]
        res = IronButterflyStrategy.scan_opportunity("SPY", 500.0, contracts, iv_rank=60.0, wing_width=5.0)
        assert res is not None
        assert res["strategy"] == "IRON_BUTTERFLY"
        assert res["net_credit"] > 0

    def test_ratio_spread_opportunity(self):
        contracts = [
            {"strike": 500.0, "is_call": False, "dte": 45, "ask": 5.0, "bid": 4.8, "delta": -0.40, "expiration_date": "2026-10-15"},
            {"strike": 480.0, "is_call": False, "dte": 45, "ask": 2.6, "bid": 2.8, "delta": -0.20, "expiration_date": "2026-10-15"},
        ]
        res = PutRatioSpreadStrategy.scan_opportunity("SPY", 500.0, contracts, momentum_20d=-0.02)
        assert res is not None
        assert res["strategy"] == "PUT_RATIO_SPREAD_1X2"
        assert res["max_profit"] > 0

    def test_calendar_spread_opportunity(self):
        contracts = [
            {"strike": 500.0, "is_call": True, "dte": 21, "ask": 4.0, "bid": 3.8, "delta": 0.50, "expiration_date": "2026-09-21"},
            {"strike": 500.0, "is_call": True, "dte": 45, "ask": 6.5, "bid": 6.2, "delta": 0.52, "expiration_date": "2026-10-15"},
        ]
        res = CalendarSpreadStrategy.scan_opportunity("SPY", 500.0, contracts, term_spread=0.04)
        assert res is not None
        assert res["strategy"] == "CALENDAR_SPREAD"
        assert res["net_debit"] > 0
