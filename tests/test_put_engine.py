"""
tests/test_put_engine.py
========================
Unit tests for PutStrategyEngine (Cash-Secured Puts, Protective Puts, Bear Put Spreads).
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.strategy.put_engine import PutStrategyEngine
from backtest.option_chain_sim import OptionChainSimulator


class TestPutStrategyEngine:
    def test_scan_cash_secured_put(self):
        engine = PutStrategyEngine()
        sim = OptionChainSimulator()
        chain = sim.generate_chain("SPY", 500.0, atm_iv=0.22, target_dtes=[30])

        proposal = engine.scan_cash_secured_put(
            symbol="SPY",
            spot=500.0,
            equity=100000.0,
            chain_contracts=chain,
            iv_rank=45.0,
            target_delta=-0.30,
            target_dte=30,
        )

        assert proposal is not None
        assert proposal.strategy == "CASH_SECURED_PUT"
        assert proposal.symbol == "SPY"
        assert proposal.collateral_required_dollars == proposal.strike * 100
        assert proposal.breakeven_price < proposal.strike
        assert proposal.theta_per_day > 0.0
        assert proposal.zero_bridge_status == "0_NS_SYNC"

    def test_scan_protective_put(self):
        engine = PutStrategyEngine()
        sim = OptionChainSimulator()
        chain = sim.generate_chain("QQQ", 440.0, atm_iv=0.25, target_dtes=[60])

        # Inverted term structure triggers tail hedge
        proposal = engine.scan_protective_put(
            symbol="QQQ",
            spot=440.0,
            chain_contracts=chain,
            term_structure_inverted=True,
            target_delta=-0.15,
            target_dte=60,
        )

        assert proposal is not None
        assert proposal.strategy == "PROTECTIVE_PUT"
        assert proposal.strike < 440.0
        assert proposal.max_loss_dollars > 0.0
        assert proposal.delta < 0.0

    def test_scan_bear_put_spread(self):
        engine = PutStrategyEngine()
        sim = OptionChainSimulator()
        chain = sim.generate_chain("TSLA", 200.0, atm_iv=0.50, target_dtes=[45])

        res = engine.scan_bear_put_spread(
            symbol="TSLA",
            spot=200.0,
            chain_contracts=chain,
            bearish_momentum_score=0.035,
            target_dte=45,
        )

        assert res is not None
        assert res["strategy"] == "BEAR_PUT_SPREAD"
        assert res["long_strike"] > res["short_strike"]
        assert res["max_profit_dollars"] > 0.0
        assert res["risk_reward_ratio"] > 0.0
