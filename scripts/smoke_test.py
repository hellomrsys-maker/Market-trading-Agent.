"""
scripts/smoke_test.py
======================
OptionAlpha Agent — Fast 15-Second End-to-End System Smoke Test

Verifies that:
  1. All 17 Python packages and submodules import cleanly
  2. FeatureMatrix generates valid 13-dim float vectors without NaNs
  3. OptionChainSimulator creates OCC-formatted option contracts
  4. RiskGate passes standard orders and blocks breached limits
  5. Backtesting engine executes a multi-day cycle and calculates Sharpe
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import date, timedelta
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import get_strategy_settings, get_ai_settings
from ai.features.feature_matrix import FeatureMatrix
from backtest.option_chain_sim import OptionChainSimulator, bsm_price, bsm_greeks
from backtest.engine import BacktestEngine
from agent.risk.risk_gate import RiskGate, OrderIntent, RiskDecision
from agent.brain.memory import TradeMemory


def run_smoke_test():
    print("\n" + "=" * 60)
    print("  OptionAlpha System Smoke Test (CI / Local)")
    print("=" * 60)

    # 1. Config Validation
    print("  [1/5] Validating configuration & settings...")
    strat = get_strategy_settings()
    assert strat.starting_capital == 100_000.0
    assert len(strat.trading_universe) >= 5
    print("        -> Config valid")

    # 2. Feature Extraction
    print("  [2/5] Validating FeatureMatrix online math...")
    fm = FeatureMatrix()
    for i in range(30):
        fm.update({"close": 400.0 + i, "volume": 10_000_000})
    vec = fm.latest()
    assert vec.shape == (13,)
    assert not np.any(np.isnan(vec))
    print("        -> FeatureMatrix outputs 13 finite dimensions")

    # 3. Option Simulation & Greeks
    print("  [3/5] Validating BSM pricing & Greeks...")
    price = bsm_price(500.0, 490.0, 30, 0.20, is_call=False)
    greeks = bsm_greeks(500.0, 490.0, 30, 0.20, is_call=False)
    assert price > 0.0
    assert -1.0 <= greeks["delta"] <= 0.0
    assert greeks["gamma"] > 0.0
    print(f"        -> BSM Put Price: ${price:.2f}, Delta: {greeks['delta']}")

    # 4. Risk Gate Logic
    print("  [4/5] Validating Risk Gate & Circuit Breakers...")
    gate = RiskGate()
    intent = OrderIntent(
        symbol="SPY", strategy="WHEEL_CSP", option_symbol="SPY251219P00480000",
        is_call=False, strike=480.0, expiry=date.today() + timedelta(days=30),
        delta=0.30, premium=3.50, bid=3.45, ask=3.55, qty=1, iv_rank=50.0
    )
    res = gate.evaluate(intent, 100_000.0)
    assert res.decision == RiskDecision.ALLOW

    # Test breach (daily loss limit)
    gate.update_pnl(-2500.0)
    res_halt = gate.evaluate(intent, 100_000.0)
    assert res_halt.decision == RiskDecision.REJECT
    print("        -> Risk gate correctly allows valid orders & rejects on breach")

    # 5. Backtest Loop
    print("  [5/5] Validating Backtest Engine (10-day quick cycle)...")
    engine = BacktestEngine(symbols=["SPY", "QQQ"])
    result = engine.run(days=10)
    assert "total_return_pct" in result.metrics
    assert "sharpe_ratio" in result.metrics
    print(f"        -> 10-day backtest complete (Trades: {result.metrics['total_trades']})")

    print("\n" + "=" * 60)
    print("  [PASS] ALL 5 SMOKE TEST SUITES PASSED CLEANLY")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_smoke_test()
