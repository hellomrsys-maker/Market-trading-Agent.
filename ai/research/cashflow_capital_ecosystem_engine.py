"""
Top-Down Cash Flow & Capital Ecosystem Engine (Module Z1 - Python)
Synthesizes the financial structuring frameworks of Emma Edwards (Good With Money):
- Top-Down Flowchart Routing (Income -> Spend Channel vs Keep/Save Channel)
- Expense Streamlining & Payday Neutrality
- Multi-Timeline Sinking Fund Amortization with inflation/interest buffers
- CJI Framework (Categorisation, Joy 1-10 heatmap, Intentionality Audit)
- Money Leak Litmus Test
- PMAE Ecosystem Governance (Permission, Margin for Error / New Zero Buffer, Autonomy, Ease)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import math


@dataclass
class SinkingFund:
    name: str
    target_amount: float
    periods_remaining: int
    buffer_percent: float = 0.10  # 10% margin buffer

    def calculate_installment(self) -> float:
        if self.periods_remaining <= 0:
            return self.target_amount * (1.0 + self.buffer_percent)
        total_needed = self.target_amount * (1.0 + self.buffer_percent)
        return total_needed / float(self.periods_remaining)


@dataclass
class CJITransaction:
    id: str
    amount: float
    category: str
    is_essential: bool
    joy_ranking: int         # 1 to 10 scale
    is_intentional: bool     # True if planned, False if impulsive/passive


@dataclass
class CapitalEcosystemState:
    total_income: float
    fixed_essentials: float
    variable_essentials: float
    sinking_funds_total: float
    workable_total: float
    keep_savings_allocated: float
    spend_discretionary_allocated: float
    new_zero_buffer: float = 100.0


class CashflowCapitalEcosystemEngine:
    """
    Module Z1: Top-Down Cash Flow & Capital Ecosystem Engine.
    Enforces payday neutrality, streamlines operational budgets, tracks sinking funds, and audits money leaks.
    """

    def __init__(self, baseline_new_zero: float = 100.0):
        self.new_zero_buffer = baseline_new_zero
        self.sinking_funds: Dict[str, SinkingFund] = {}
        self.transactions: List[CJITransaction] = []

    def add_sinking_fund(self, name: str, target: float, periods: int, buffer: float = 0.10):
        self.sinking_funds[name] = SinkingFund(
            name=name, target_amount=target, periods_remaining=periods, buffer_percent=buffer
        )

    def calculate_streamlined_ecosystem(
        self,
        income: float,
        fixed_costs: float,
        variable_costs: float,
        savings_ratio: float = 0.20
    ) -> CapitalEcosystemState:
        """
        Executes Top-Down flow: Income -> Essentials & Sinking Funds -> Workable Total -> Keep (Pay Yourself First) vs Spend.
        """
        # 1. Total sinking fund periodic installments
        sinking_installment_total = sum(sf.calculate_installment() for sf in self.sinking_funds.values())

        # 2. Total essential obligations
        total_essentials = fixed_costs + variable_costs + sinking_installment_total

        # 3. Workable Total = Income - Essentials
        workable = max(0.0, income - total_essentials)

        # 4. Pay Yourself First: Keep Allocation
        keep_alloc = workable * savings_ratio

        # 5. Spend Allocation (Discretionary)
        spend_alloc = max(0.0, workable - keep_alloc)

        return CapitalEcosystemState(
            total_income=income,
            fixed_essentials=fixed_costs,
            variable_essentials=variable_costs,
            sinking_funds_total=round(sinking_installment_total, 2),
            workable_total=round(workable, 2),
            keep_savings_allocated=round(keep_alloc, 2),
            spend_discretionary_allocated=round(spend_alloc, 2),
            new_zero_buffer=self.new_zero_buffer
        )

    def execute_money_leak_litmus_test(
        self,
        category: str,
        estimated_frequency: int,
        estimated_spend: float,
        actual_frequency: int,
        actual_spend: float
    ) -> Dict[str, Any]:
        """
        Calculates behavioural leak discrepancy between perceived and actual spending.
        """
        freq_diff = actual_frequency - estimated_frequency
        spend_leak = actual_spend - estimated_spend
        is_leaking = spend_leak > 0.0 or freq_diff > 0

        return {
            "category": category,
            "frequency_discrepancy": freq_diff,
            "monetary_leak_amount": round(spend_leak, 2),
            "is_leaking": is_leaking,
            "hilss_potential": round(max(0.0, spend_leak), 2)  # High-Impact Low-Sacrifice Savings
        }

    def evaluate_cji_heatmap(self, transactions: List[CJITransaction]) -> Dict[str, Any]:
        """
        Computes CJI metrics: Categorisation ratios, Joy Heatmap score, and Intentionality percentage.
        """
        if not transactions:
            return {"total_transactions": 0, "intentional_ratio": 1.0, "avg_joy_score": 10.0}

        total_spend = sum(t.amount for t in transactions)
        intentional_spend = sum(t.amount for t in transactions if t.is_intentional)
        total_joy_weighted = sum(t.amount * t.joy_ranking for t in transactions)

        intentional_ratio = intentional_spend / total_spend if total_spend > 0 else 1.0
        weighted_joy = total_joy_weighted / total_spend if total_spend > 0 else 10.0

        return {
            "total_transactions": len(transactions),
            "total_spend": round(total_spend, 2),
            "intentional_spend_ratio": round(intentional_ratio, 4),
            "weighted_joy_heatmap_score": round(weighted_joy, 2),
            "is_values_aligned": intentional_ratio >= 0.80 and weighted_joy >= 7.0
        }
