"""
tests/test_call_engine.py
=========================
Unit tests for CallStrategyEngine (Long Calls, Covered Calls, Bull Call Spreads).
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.strategy.call_engine import CallStrategyEngine
from backtest.option_chain_sim import OptionChainSimulator


class TestCallStrategyEngine:
    def test_scan_long_call_momentum(self):
        engine = CallStrategyEngine()
        sim = OptionChainSimulator()
        chain = sim.generate_chain("SPY", 500.0, atm_iv=0.20, target_dtes=[45])

        # Positive momentum (3% return)
        proposal = engine.scan_long_call(
            symbol="SPY",
            spot=500.0,
            chain_contracts=chain,
            bullish_momentum_score=0.03,
            target_delta=0.50,
            target_dte=45,
        )

        assert proposal is not None
        assert proposal.strategy == "LONG_CALL"
        assert proposal.symbol == "SPY"
        assert proposal.breakeven_price > proposal.strike
        assert proposal.max_loss_dollars > 0.0
        assert proposal.zero_bridge_status == "0_NS_SYNC"

    def test_scan_covered_call_strike_above_basis(self):
        engine = CallStrategyEngine()
        sim = OptionChainSimulator()
        chain = sim.generate_chain("AAPL", 180.0, atm_iv=0.22, target_dtes=[30])

        proposal = engine.scan_covered_call(
            symbol="AAPL",
            spot=180.0,
            cost_basis=175.0,  # Basis is below current spot
            chain_contracts=chain,
            target_delta=0.20,
            target_dte=30,
        )

        assert proposal is not None
        assert proposal.strategy == "COVERED_CALL"
        assert proposal.strike >= 175.0
        assert proposal.max_profit_dollars > 0.0
        assert proposal.theta_per_day > 0.0

    def test_scan_bull_call_spread(self):
        engine = CallStrategyEngine()
        sim = OptionChainSimulator()
        chain = sim.generate_chain("MSFT", 420.0, atm_iv=0.25, target_dtes=[45])

        res = engine.scan_bull_call_spread(
            symbol="MSFT",
            spot=420.0,
            chain_contracts=chain,
            bullish_momentum_score=0.025,
            target_dte=45,
        )

        assert res is not None
        assert res["strategy"] == "BULL_CALL_SPREAD"
        assert res["short_strike"] > res["long_strike"]
        assert res["max_profit_dollars"] > 0.0
        assert res["risk_reward_ratio"] > 0.0
