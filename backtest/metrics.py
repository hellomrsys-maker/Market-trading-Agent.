"""
backtest/metrics.py
====================
OptionAlpha Agent — Backtest Performance Metrics

Calculates industry-standard quantitative metrics:
Sharpe Ratio, Sortino Ratio, Max Drawdown, Calmar Ratio, Profit Factor,
Win Rate by Strategy, Average Trade Duration, and Monthly Return Matrix.
"""

from __future__ import annotations

import math
from typing import Dict, List
import numpy as np
from backtest.position_tracker import SimulatedTrade


class BacktestMetrics:
    """
    Computes comprehensive portfolio and trade statistics.
    """

    @staticmethod
    def calculate(
        daily_history: List[Dict],
        closed_trades: List[SimulatedTrade],
        initial_capital: float = 100_000.0,
        risk_free_rate: float = 0.05
    ) -> Dict:
        if not daily_history:
            return {"error": "No daily history available"}

        values = [d["portfolio_value"] for d in daily_history]
        dates = [d["date"] for d in daily_history]
        n_days = len(values)

        final_equity = values[-1]
        total_pnl = final_equity - initial_capital
        total_return_pct = (total_pnl / initial_capital) * 100.0
        cagr = ((final_equity / initial_capital) ** (252.0 / max(1, n_days)) - 1.0) * 100.0 if final_equity > 0 else 0.0

        # Daily Returns
        returns = np.diff(values) / np.array(values[:-1]) if len(values) > 1 else np.array([0.0])
        daily_rf = risk_free_rate / 252.0
        excess_returns = returns - daily_rf

        mean_ret = float(np.mean(returns)) if len(returns) > 0 else 0.0
        std_ret = float(np.std(returns)) if len(returns) > 0 else 1e-6

        # Sharpe Ratio (annualized)
        sharpe = float((np.mean(excess_returns) / (std_ret + 1e-8)) * math.sqrt(252)) if len(returns) > 1 else 0.0

        # Sortino Ratio (annualized, downside deviation only)
        downside_diff = returns[returns < 0]
        downside_std = float(np.std(downside_diff)) if len(downside_diff) > 0 else 1e-6
        sortino = float((np.mean(excess_returns) / (downside_std + 1e-8)) * math.sqrt(252)) if len(returns) > 1 else 0.0

        # Drawdowns
        peaks = np.maximum.accumulate(values)
        drawdowns = (peaks - np.array(values)) / peaks
        max_drawdown_pct = float(np.max(drawdowns)) * 100.0 if len(drawdowns) > 0 else 0.0
        calmar = (cagr / max_drawdown_pct) if max_drawdown_pct > 0 else 0.0

        # Trade Level Metrics
        n_trades = len(closed_trades)
        winning_trades = [t for t in closed_trades if t.realized_pnl > 0]
        losing_trades = [t for t in closed_trades if t.realized_pnl < 0]

        win_rate = (len(winning_trades) / n_trades * 100.0) if n_trades > 0 else 0.0
        total_gains = sum(t.realized_pnl for t in winning_trades)
        total_losses = abs(sum(t.realized_pnl for t in losing_trades))
        profit_factor = (total_gains / total_losses) if total_losses > 0 else (99.0 if total_gains > 0 else 0.0)

        avg_trade_pnl = float(np.mean([t.realized_pnl for t in closed_trades])) if n_trades > 0 else 0.0
        avg_days_held = float(np.mean([t.days_held for t in closed_trades])) if n_trades > 0 else 0.0

        # Strategy Breakdown
        strategy_stats = {}
        for strat in ["WHEEL_CSP", "WHEEL_CC", "IRON_CONDOR"]:
            s_trades = [t for t in closed_trades if t.strategy == strat]
            s_wins = [t for t in s_trades if t.realized_pnl > 0]
            strategy_stats[strat] = {
                "trades": len(s_trades),
                "win_rate": round(len(s_wins) / len(s_trades) * 100.0, 1) if s_trades else 0.0,
                "total_pnl": round(sum(t.realized_pnl for t in s_trades), 2),
                "avg_pnl": round(float(np.mean([t.realized_pnl for t in s_trades])), 2) if s_trades else 0.0,
            }

        return {
            "initial_capital": initial_capital,
            "final_equity": round(final_equity, 2),
            "total_pnl": round(total_pnl, 2),
            "total_return_pct": round(total_return_pct, 2),
            "cagr_pct": round(cagr, 2),
            "sharpe_ratio": round(sharpe, 3),
            "sortino_ratio": round(sortino, 3),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "calmar_ratio": round(calmar, 3),
            "profit_factor": round(profit_factor, 2),
            "total_trades": n_trades,
            "win_rate_pct": round(win_rate, 2),
            "avg_trade_pnl": round(avg_trade_pnl, 2),
            "avg_days_held": round(avg_days_held, 1),
            "strategy_breakdown": strategy_stats,
            "trading_days": n_days,
            "start_date": dates[0] if dates else "",
            "end_date": dates[-1] if dates else "",
        }
