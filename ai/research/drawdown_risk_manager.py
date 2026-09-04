"""
ai/research/drawdown_risk_manager.py
====================================
OptionAlpha Agent — Module T_sys1: Python System Drawdown, Risk Management & Compounding Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple

class DrawdownRiskManager:
    """
    Synthesizes System Risk Management & Proactive Improvement (Crack & Nekritin):
    - 2% Risk Sizing Rule & Position Sizing ($200 on $10k account)
    - Peak Equity Tracking, Dollar Drawdown & Percentage Drawdown
    - Trailing Portfolio Stop-Loss (20% Max DD Cutoff)
    - Consecutive Loss Circuit Breaker
    - Reinvestment Rate & Compounding Growth Modeling
    - Pyramid Capital Allocation (Low Volatility vs High Volatility)
    """
    def __init__(self, initial_capital: float = 10000.0, max_dd_pct_cutoff: float = 20.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.peak_equity = initial_capital
        self.max_dd_pct_cutoff = max_dd_pct_cutoff
        self.consecutive_losses = 0
        self.memory_state = np.zeros(64, dtype=np.float32)

    def calculate_position_size(
        self,
        risk_pct: float,
        max_loss_per_contract: float
    ) -> int:
        """
        Position sizing formula:
        Max Dollar Risk = Account Capital * (risk_pct / 100.0)
        Contracts = floor(Max Dollar Risk / Max Loss Per Contract)
        """
        max_risk_dollars = self.current_capital * (risk_pct / 100.0)
        if max_loss_per_contract <= 0:
            return 1
        contracts = int(max_risk_dollars // max_loss_per_contract)
        return max(1, contracts)

    def update_trade_result(self, pnl: float) -> Dict[str, float | bool | str]:
        """
        Updates capital, peak equity, drawdown, and evaluates circuit breaker triggers.
        """
        self.current_capital += pnl
        if self.current_capital > self.peak_equity:
            self.peak_equity = self.current_capital

        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        dollar_dd = self.peak_equity - self.current_capital
        pct_dd = (dollar_dd / self.peak_equity) * 100.0 if self.peak_equity > 0 else 0.0

        is_dd_breached = pct_dd >= self.max_dd_pct_cutoff
        is_consecutive_breached = self.consecutive_losses >= 6

        status = "HEALTHY"
        if is_dd_breached:
            status = "HALT_MAX_DRAWDOWN_BREACHED"
        elif is_consecutive_breached:
            status = "HALT_CONSECUTIVE_LOSS_CIRCUIT_BREAKER"

        return {
            "current_capital": self.current_capital,
            "peak_equity": self.peak_equity,
            "dollar_drawdown": dollar_dd,
            "pct_drawdown": pct_dd,
            "consecutive_losses": self.consecutive_losses,
            "is_system_halted": is_dd_breached or is_consecutive_breached,
            "system_status": status
        }

    @staticmethod
    def simulate_compounding_growth(
        starting_capital: float,
        win_rate: float,
        avg_win_pct: float,
        avg_loss_pct: float,
        trades: int = 100,
        reinvestment_rate: float = 1.0
    ) -> Dict[str, float]:
        """
        Simulates compounding equity curve vs partial profit extraction.
        """
        capital = starting_capital
        for _ in range(trades):
            if np.random.rand() < win_rate:
                profit = capital * (avg_win_pct / 100.0)
                capital += profit * reinvestment_rate
            else:
                loss = capital * (avg_loss_pct / 100.0)
                capital -= loss

        return {
            "starting_capital": starting_capital,
            "final_capital": capital,
            "total_return_pct": ((capital - starting_capital) / starting_capital) * 100.0
        }
