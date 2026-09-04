"""
tests/test_memory.py
=====================
Unit tests for the agent's episodic trade memory.
Fully offline — no Alpaca API calls.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.brain.memory import TradeMemory, TradeRecord


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def make_trade(
    symbol="SPY", strategy="WHEEL_CSP", pnl=250.0,
    days_ago=0, iv_rank=55.0, regime="Neutral"
) -> TradeRecord:
    today     = date.today()
    closed_at = str(today - timedelta(days=days_ago))
    opened_at = str(today - timedelta(days=days_ago + 30))
    premium   = 500.0
    return TradeRecord(
        symbol           = symbol,
        strategy         = strategy,
        option_symbol    = f"{symbol}250101P00100000",
        strike           = 100.0,
        expiry           = str(today + timedelta(days=20)),
        dte_at_open      = 30,
        premium_received = premium,
        pnl              = pnl,
        pnl_pct          = pnl / premium,
        opened_at        = opened_at,
        closed_at        = closed_at,
        days_held        = 30,
        close_reason     = "profit_take" if pnl > 0 else "stop_loss",
        iv_rank_at_open  = iv_rank,
        regime_at_open   = regime,
        ensemble_signal  = 0.7,
        ensemble_conf    = 0.8,
    )


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def mem(tmp_path) -> TradeMemory:
    return TradeMemory(capacity=50, persist_path=tmp_path / "memory.json")


# ─────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────

class TestTradeRecord:
    def test_profitable_flag_set(self):
        t = make_trade(pnl=100.0)
        assert t.was_profitable is True

    def test_not_profitable_flag(self):
        t = make_trade(pnl=-50.0)
        assert t.was_profitable is False

    def test_zero_pnl_not_profitable(self):
        t = make_trade(pnl=0.0)
        assert t.was_profitable is False


class TestTradeMemoryBasics:
    def test_empty_memory(self, mem):
        assert len(mem) == 0

    def test_record_increases_count(self, mem):
        mem.record(make_trade())
        assert len(mem) == 1

    def test_recent_returns_correct_n(self, mem):
        for i in range(10):
            mem.record(make_trade(pnl=100.0 * (i + 1)))
        recent = mem.recent(5)
        assert len(recent) == 5

    def test_recent_is_newest_first(self, mem):
        mem.record(make_trade(pnl=100.0))
        mem.record(make_trade(pnl=200.0))
        recent = mem.recent(2)
        assert recent[-1].pnl == pytest.approx(200.0)

    def test_capacity_respected(self, tmp_path):
        mem = TradeMemory(capacity=5, persist_path=tmp_path / "cap_test.json")
        for i in range(10):
            mem.record(make_trade(pnl=float(i)))
        assert len(mem) == 5

    def test_by_symbol_filters(self, mem):
        mem.record(make_trade(symbol="SPY"))
        mem.record(make_trade(symbol="QQQ"))
        mem.record(make_trade(symbol="SPY"))
        spy_trades = mem.by_symbol("SPY")
        assert all(t.symbol == "SPY" for t in spy_trades)
        assert len(spy_trades) == 2


class TestWinRate:
    def test_all_profitable(self, mem):
        for _ in range(5):
            mem.record(make_trade(pnl=100.0))
        assert mem.win_rate(5) == pytest.approx(1.0)

    def test_all_losses(self, mem):
        for _ in range(5):
            mem.record(make_trade(pnl=-100.0))
        assert mem.win_rate(5) == pytest.approx(0.0)

    def test_mixed_50_pct(self, mem):
        for i in range(10):
            mem.record(make_trade(pnl=100.0 if i % 2 == 0 else -100.0))
        assert mem.win_rate(10) == pytest.approx(0.5)

    def test_empty_returns_neutral_prior(self, mem):
        assert mem.win_rate() == pytest.approx(0.5)

    def test_symbol_win_rate(self, mem):
        mem.record(make_trade(symbol="NVDA", pnl=200.0))
        mem.record(make_trade(symbol="NVDA", pnl=-100.0))
        mem.record(make_trade(symbol="AAPL", pnl=-50.0))
        assert mem.symbol_win_rate("NVDA") == pytest.approx(0.5)
        assert mem.symbol_win_rate("AAPL") == pytest.approx(0.0)
        assert mem.symbol_win_rate("NEW")  == pytest.approx(0.5)  # prior


class TestMemoryFeatures:
    def test_returns_4_features(self, mem):
        for _ in range(5):
            mem.record(make_trade(pnl=100.0))
        feats = mem.get_memory_features("SPY")
        assert len(feats) == 4

    def test_all_finite(self, mem):
        for _ in range(5):
            mem.record(make_trade(pnl=100.0))
        feats = mem.get_memory_features("SPY")
        import math
        assert all(math.isfinite(f) for f in feats)

    def test_all_in_expected_range(self, mem):
        for _ in range(5):
            mem.record(make_trade(pnl=100.0))
        feats = mem.get_memory_features("SPY")
        assert 0.0 <= feats[0] <= 1.0   # win_rate
        assert -1.0 <= feats[1] <= 1.0  # avg_pnl_pct (clipped)
        assert 0.0 <= feats[2] <= 1.0   # symbol_win_rate
        assert 0.0 <= feats[3] <= 1.0   # days_since (normalised)


class TestStrategyStats:
    def test_stats_all_strategies(self, mem):
        mem.record(make_trade(strategy="WHEEL_CSP",  pnl=100.0))
        mem.record(make_trade(strategy="WHEEL_CC",   pnl=-50.0))
        mem.record(make_trade(strategy="IRON_CONDOR",pnl=200.0))
        s = mem.strategy_stats()
        assert "WHEEL_CSP"   in s
        assert "WHEEL_CC"    in s
        assert "IRON_CONDOR" in s
        assert s["WHEEL_CSP"]["count"] == 1
        assert s["WHEEL_CSP"]["win_rate"] == pytest.approx(1.0)
        assert s["WHEEL_CC"]["win_rate"]  == pytest.approx(0.0)


class TestPersistence:
    def test_save_and_reload(self, tmp_path):
        path = tmp_path / "persist_test.json"
        m1   = TradeMemory(capacity=50, persist_path=path)
        m1.record(make_trade(pnl=100.0, symbol="SPY"))
        m1.record(make_trade(pnl=200.0, symbol="QQQ"))

        m2 = TradeMemory(capacity=50, persist_path=path)
        assert len(m2) == 2
        assert m2.recent(2)[0].symbol == "SPY"
        assert m2.recent(2)[1].symbol == "QQQ"

    def test_corrupt_file_gracefully_handled(self, tmp_path):
        path = tmp_path / "corrupt.json"
        path.write_text("NOT VALID JSON {{{")
        # Should not raise
        mem = TradeMemory(capacity=50, persist_path=path)
        assert len(mem) == 0
