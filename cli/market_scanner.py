"""
cli/market_scanner.py
======================
OptionAlpha Agent — Interactive Market & Volatility Scanner

Usage:
    python -m cli.market_scanner
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.collector import DataCollector
from ai.features.feature_matrix import FeatureMatrix, bars_from_alpaca


def main():
    print("\n" + "=" * 60)
    print("  OptionAlpha — Implied Volatility & Momentum Scanner")
    print("=" * 60)

    symbols = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMD", "AMZN"]
    collector = DataCollector()

    print(f"\n{'Symbol':<8} {'Close':<10} {'20d Ret':<10} {'IV Rank':<10} {'RV20':<10} {'Action'}")
    print("-" * 60)

    for sym in symbols:
        bars = collector.load_bars(sym)
        if not bars:
            bars = collector._synthetic_bars(sym, 60)
        std_bars = bars_from_alpaca(bars)

        fm = FeatureMatrix()
        for b in std_bars:
            fm.update(b)
        feats = fm.latest()

        close = std_bars[-1]["close"]
        ret20 = feats[2] * 100.0
        iv_rank = feats[7]
        rv20 = feats[5] * 100.0

        if iv_rank >= 35.0:
            rec = "IRON CONDOR (High IV)"
        elif iv_rank >= 15.0:
            rec = "WHEEL CSP"
        else:
            rec = "HOLD / PASS"

        print(f"{sym:<8} ${close:<9.2f} {ret20:>+5.1f}%     {iv_rank:>5.1f}      {rv20:>5.1f}%     {rec}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
