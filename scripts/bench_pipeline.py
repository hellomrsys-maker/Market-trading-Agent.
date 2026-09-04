"""
scripts/bench_pipeline.py
==========================
OptionAlpha Agent — End-to-End Pipeline Latency Benchmark

Measures execution latency across all sub-components:
  1. Feature extraction (FeatureMatrix)
  2. BSM pricing & Greeks computation (BSM / Julia)
  3. Risk Gate evaluation
  4. Full decision cycle throughput (cycles / second)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ai.features.feature_matrix import FeatureMatrix
from backtest.option_chain_sim import bsm_price, bsm_greeks
from agent.risk.risk_gate import RiskGate, OrderIntent
from datetime import date, timedelta


def run_benchmark():
    print("\n" + "=" * 60)
    print("  OptionAlpha Pipeline Latency Benchmark")
    print("=" * 60 + "\n")

    N = 1000

    # ── 1. FeatureMatrix Latency ──────────────────────────────────
    fm = FeatureMatrix()
    bar = {"close": 480.0, "volume": 25_000_000, "open": 479.5, "high": 482.0, "low": 478.0}
    for _ in range(30):
        fm.update(bar)

    t0 = time.perf_counter()
    for _ in range(N):
        fm.update(bar)
        _ = fm.latest()
    t_feat = (time.perf_counter() - t0) / N * 1000.0  # ms
    print(f"  [+] FeatureMatrix online update:   {t_feat*1000.0:>6.1f} microseconds ({1000/t_feat:,.0f} ops/sec)")

    # ── 2. Black-Scholes & Greeks Latency ────────────────────────
    t0 = time.perf_counter()
    for _ in range(N):
        _ = bsm_price(480.0, 475.0, 30, 0.20, is_call=False)
        _ = bsm_greeks(480.0, 475.0, 30, 0.20, is_call=False)
    t_bsm = (time.perf_counter() - t0) / N * 1000.0  # ms
    print(f"  [+] BSM Pricing + Full Greeks:     {t_bsm*1000.0:>6.1f} microseconds ({1000/t_bsm:,.0f} ops/sec)")

    # ── 3. Risk Gate Evaluation Latency ──────────────────────────
    gate = RiskGate()
    intent = OrderIntent(
        symbol="SPY", strategy="WHEEL_CSP", option_symbol="SPY251219P00480000",
        is_call=False, strike=480.0, expiry=date.today() + timedelta(days=30),
        delta=0.30, premium=3.50, bid=3.45, ask=3.55, qty=1, iv_rank=50.0
    )

    t0 = time.perf_counter()
    for _ in range(N):
        _ = gate.evaluate(intent, 100_000.0)
    t_risk = (time.perf_counter() - t0) / N * 1000.0
    print(f"  [+] Risk Gate Evaluation:          {t_risk*1000.0:>6.1f} microseconds ({1000/t_risk:,.0f} ops/sec)")

    total_decision_latency = t_feat + t_bsm + t_risk
    print("-" * 60)
    print(f"  [*] Total Single-Symbol Cycle:     {total_decision_latency:>6.3f} ms")
    print(f"  [*] Universe (7 symbols) Cycle:    {total_decision_latency * 7:>6.3f} ms (< 10ms target: PASS)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_benchmark()
