"""
backtest/run_backtest.py
=========================
OptionAlpha Agent — Backtest CLI Runner

Usage:
    python -m backtest.run_backtest
    python -m backtest.run_backtest --days 252 --symbols SPY QQQ NVDA
    python -m backtest.run_backtest --smoke-test
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is in PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backtest.engine import BacktestEngine
from backtest.report import BacktestReportGenerator
from loguru import logger


def parse_args():
    parser = argparse.ArgumentParser(description="Run OptionAlpha Strategy Backtest")
    parser.add_argument("--days", type=int, default=504, help="Number of trading days to simulate")
    parser.add_argument("--capital", type=float, default=100_000.0, help="Initial portfolio capital ($)")
    parser.add_argument("--symbols", nargs="+", default=None, help="Universe symbols to trade")
    parser.add_argument("--smoke-test", action="store_true", help="Quick 30-day run for CI/validation")
    return parser.parse_args()


def main():
    args = parse_args()
    days = 30 if args.smoke_test else args.days

    engine = BacktestEngine(
        symbols=args.symbols,
        initial_capital=args.capital,
    )

    result = engine.run(days=days)
    report_path = BacktestReportGenerator.generate(result)

    print("\n" + "=" * 60)
    print(f"  [OK] Backtest Complete ({days} days)")
    print(f"  * Total Return: {result.metrics.get('total_return_pct'):+.2f}%")
    print(f"  * Sharpe Ratio: {result.metrics.get('sharpe_ratio'):.3f}")
    print(f"  * Max Drawdown: {result.metrics.get('max_drawdown_pct'):.2f}%")
    print(f"  * Win Rate:     {result.metrics.get('win_rate_pct'):.1f}% ({result.metrics.get('total_trades')} trades)")
    print(f"  * Report Saved: {report_path}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
