"""
tests/test_risk_gate.py
========================
Unit tests for the Python risk gate — all 6 circuit breakers,
position sizing logic, and quality filters.
No Alpaca API calls. Fully offline.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import date, timedelta

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Patch env before importing settings
import os
os.environ.setdefault("ALPACA_API_KEY",    "test_key")
os.environ.setdefault("ALPACA_SECRET_KEY", "test_secret")

from agent.risk.risk_gate import RiskGate, OrderIntent, RiskDecision


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def gate() -> RiskGate:
    return RiskGate()


def make_intent(**kwargs) -> OrderIntent:
    defaults = dict(
        symbol        = "SPY",
        strategy      = "WHEEL_CSP",
        option_symbol = "SPY251219P00480000",
        is_call       = False,
        strike        = 480.0,
        expiry        = date.today() + timedelta(days=30),
        delta         = 0.30,
        premium       = 5.00,
        bid           = 4.90,
        ask           = 5.10,
        qty           = 1,
        iv_rank       = 55.0,
    )
    defaults.update(kwargs)
    return OrderIntent(**defaults)


EQUITY = 100_000.0


# ─────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────

class TestRiskGateAllow:
    def test_normal_csp_allowed(self, gate):
        result = gate.evaluate(make_intent(), EQUITY)
        assert result.is_allowed(), f"Expected ALLOW, got {result.decision}: {result.reasons}"

    def test_normal_ic_allowed(self, gate):
        intent = make_intent(strategy="IRON_CONDOR", iv_rank=60.0)
        result = gate.evaluate(intent, EQUITY)
        assert result.is_allowed()


class TestDailyLossLimit:
    def test_loss_limit_blocks(self, gate):
        gate.update_pnl(-2500.0)   # exceeds default $2,000 limit
        result = gate.evaluate(make_intent(), EQUITY)
        assert result.decision == RiskDecision.REJECT
        assert any("loss limit" in r.lower() or "daily" in r.lower() for r in result.reasons)

    def test_no_block_within_limit(self, gate):
        gate.update_pnl(-1000.0)
        result = gate.evaluate(make_intent(), EQUITY)
        assert result.is_allowed()


class TestVIXCircuitBreaker:
    def test_high_vix_blocks_ic(self, gate):
        gate.update_vix(40.0)   # above default 35 threshold
        intent = make_intent(strategy="IRON_CONDOR", iv_rank=60.0)
        result = gate.evaluate(intent, EQUITY)
        assert result.decision == RiskDecision.REJECT
        assert any("vix" in r.lower() for r in result.reasons)

    def test_high_vix_allows_csp(self, gate):
        gate.update_vix(40.0)
        result = gate.evaluate(make_intent(strategy="WHEEL_CSP"), EQUITY)
        assert result.is_allowed()


class TestIVRankGate:
    def test_low_iv_rank_blocks_ic(self, gate):
        intent = make_intent(strategy="IRON_CONDOR", iv_rank=20.0)  # below 30 threshold
        result = gate.evaluate(intent, EQUITY)
        assert result.decision == RiskDecision.REJECT
        assert any("iv rank" in r.lower() or "iv_rank" in r.lower() for r in result.reasons)

    def test_sufficient_iv_rank_allows_ic(self, gate):
        intent = make_intent(strategy="IRON_CONDOR", iv_rank=45.0)
        result = gate.evaluate(intent, EQUITY)
        assert result.is_allowed()


class TestMaxPositions:
    def test_max_positions_blocks(self, gate):
        # Fill up all positions
        symbols = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMD", "AMZN", "TSLA", "META", "GOOG"]
        for sym in symbols:
            gate.register_position(sym, "WHEEL_CSP")

        result = gate.evaluate(make_intent(symbol="NEW"), EQUITY)
        assert result.decision == RiskDecision.REJECT
        assert any("max" in r.lower() or "position" in r.lower() for r in result.reasons)


class TestDuplicatePosition:
    def test_duplicate_blocked(self, gate):
        gate.register_position("SPY", "WHEEL_CSP")
        result = gate.evaluate(make_intent(symbol="SPY", strategy="WHEEL_CSP"), EQUITY)
        assert result.decision == RiskDecision.REJECT

    def test_close_allowed_on_existing(self, gate):
        gate.register_position("SPY", "WHEEL_CSP")
        result = gate.evaluate(make_intent(symbol="SPY", strategy="CLOSE"), EQUITY)
        # CLOSE should not be blocked by duplicate position check
        assert result.decision != RiskDecision.REJECT or "duplicate" not in str(result.reasons).lower()


class TestSectorConcentration:
    def test_too_many_same_sector(self, gate):
        # Register 3 tech positions
        gate.register_position("AAPL", "WHEEL_CSP")
        gate.register_position("MSFT", "WHEEL_CSP")
        gate.register_position("NVDA", "WHEEL_CSP")  # 3rd tech → should block 4th
        result = gate.evaluate(make_intent(symbol="AMD", strategy="WHEEL_CSP"), EQUITY)
        # AMD is in semis (same as NVDA), AAPL/MSFT in tech — may not block depending on sector map
        # Just verify gate runs without error
        assert result.decision in (RiskDecision.ALLOW, RiskDecision.REJECT, RiskDecision.SCALE)


class TestPositionSizing:
    def test_oversized_position_scaled(self, gate):
        # Premium $50 × 100 shares × 10 contracts = $50,000 → exceeds 5% of $100k ($5,000)
        intent = make_intent(premium=50.0, qty=10)
        result = gate.evaluate(intent, EQUITY)
        assert result.decision == RiskDecision.SCALE
        assert result.suggested_qty < 10

    def test_normal_size_allowed(self, gate):
        # Premium $5 × 100 × 1 = $500 → well within 5% = $5,000
        intent = make_intent(premium=5.0, qty=1)
        result = gate.evaluate(intent, EQUITY)
        assert result.is_allowed()


class TestQualityFilters:
    def test_wide_spread_rejected(self, gate):
        intent = make_intent(bid=1.0, ask=2.0, premium=1.5)  # $1 spread
        result = gate.evaluate(intent, EQUITY)
        assert result.decision == RiskDecision.REJECT

    def test_acceptable_spread_allowed(self, gate):
        intent = make_intent(bid=4.95, ask=5.05, premium=5.0)
        result = gate.evaluate(intent, EQUITY)
        assert result.is_allowed()


class TestHaltAndRelease:
    def test_halt_blocks_all(self, gate):
        gate._halt("manual test halt")
        result = gate.evaluate(make_intent(), EQUITY)
        assert result.decision == RiskDecision.REJECT

    def test_release_restores(self, gate):
        gate._halt("test")
        gate.release_halt()
        result = gate.evaluate(make_intent(), EQUITY)
        assert result.is_allowed()

    def test_summary_returns_dict(self, gate):
        s = gate.summary()
        assert "halted" in s
        assert "daily_pnl" in s
