"""
tests/test_market_research_and_tri_state.py
===========================================
Unit tests for MarketIntelligenceEngine, HistoricalMarketMemory, and TriStateDecisionEngine.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.research.market_intelligence import MarketIntelligenceEngine
from ai.research.historical_replay import HistoricalMarketMemory
from agent.strategy.tri_state_decision import ActionType, TriStateDecisionEngine
from backtest.option_chain_sim import OptionChainSimulator


class TestMarketIntelligence:
    def test_market_intelligence_analysis(self):
        sim = OptionChainSimulator()
        chain = sim.generate_chain("SPY", 500.0, atm_iv=0.22, target_dtes=[30, 45, 60])
        bars = [{"close": 500.0 * (1.0 + 0.002 * i)} for i in range(30)]

        report = MarketIntelligenceEngine.analyze_asset(
            symbol="SPY",
            spot_price=500.0,
            price_bars_60d=bars,
            chain_contracts=chain,
            current_vix=16.0,
        )

        assert report.symbol == "SPY"
        assert report.spot_price == 500.0
        assert report.atm_iv > 0.0
        assert report.realized_vol_20d >= 0.0
        assert report.recommendation_bias in {"SELL_PREMIUM", "BUY_PROTECTION", "NEUTRAL_HOLD"}


class TestHistoricalReplay:
    def test_crisis_scenario_matching(self):
        # High VIX + Inverted Skew matches 2008 GFC / 2020 Covid
        match = HistoricalMarketMemory.match_current_market(
            current_vix=60.0,
            skew_ratio=1.60,
            vrp=-0.10,
            rv20=0.65,
            term_slope=-0.12,
        )
        assert "2008" in match["top_match_name"] or "2020" in match["top_match_name"]
        assert match["similarity_score"] > 0.70

    def test_low_iv_bull_matching(self):
        # Low VIX matches 2024 Tech Momentum
        match = HistoricalMarketMemory.match_current_market(
            current_vix=13.0,
            skew_ratio=1.10,
            vrp=0.03,
            rv20=0.10,
            term_slope=0.02,
        )
        assert "2024" in match["top_match_name"]
        assert match["historical_win_rate"] >= 0.80


class TestTriStateDecisionEngine:
    def test_hold_on_vix_spike(self):
        dec = TriStateDecisionEngine.evaluate(
            symbol="SPY",
            spot_price=500.0,
            price_bars_60d=[],
            chain_contracts=[],
            active_positions=[],
            current_vix=38.0,  # > 35.0 hard halt
        )
        assert dec.action == ActionType.HOLD
        assert dec.risk_approval is False
        assert "VIX Circuit Breaker" in dec.mathematical_rationale

    def test_buy_to_close_on_profit_target(self):
        positions = [{
            "symbol": "SPY250620P00480000",
            "qty": -1,
            "avg_cost": 3.0,
            "market_value": -140.0,
            "unrealized_pl": 160.0,  # 53.3% profit
        }]
        dec = TriStateDecisionEngine.evaluate(
            symbol="SPY",
            spot_price=500.0,
            price_bars_60d=[],
            chain_contracts=[],
            active_positions=positions,
            current_vix=15.0,
        )
        assert dec.action == ActionType.BUY
        assert dec.strategy_target == "BUY_TO_CLOSE_PROFIT_TAKE"
        assert dec.expected_value_dollars == 160.0

    def test_sell_entry_on_positive_vrp(self):
        sim = OptionChainSimulator()
        chain = sim.generate_chain("NVDA", 120.0, atm_iv=0.45, target_dtes=[30, 60])
        bars = [{"close": 120.0 * (1.0 + 0.001 * i)} for i in range(30)]

        dec = TriStateDecisionEngine.evaluate(
            symbol="NVDA",
            spot_price=120.0,
            price_bars_60d=bars,
            chain_contracts=chain,
            active_positions=[],
            current_vix=18.0,
        )
        assert dec.action in {ActionType.SELL, ActionType.HOLD}
        assert dec.confidence > 0.50
