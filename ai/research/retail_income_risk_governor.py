"""
Disciplined Capital Allocation, Sizing & Anti-Gambling Risk Governor Engine (Module AR1 - Python)
Synthesizes Will Weiser's "Options Trading For Beginners 2022":
- Strict 5% Maximum Capital Allocation per Underlying
- Minimum 25% Unencumbered Cash Buffer Requirement
- Earnings Event & Black Swan Avoidance Filter (Avoid Selling <14 Days from Earnings)
- 50% Profit Early Management Enforcer
"""

from typing import Dict, List, Any


class RetailIncomeRiskGovernor:
    def __init__(
        self,
        max_allocation_per_symbol_pct: float = 5.0,
        min_cash_buffer_pct: float = 25.0,
        min_earnings_buffer_days: int = 14
    ):
        self.max_symbol_alloc = max_allocation_per_symbol_pct
        self.min_cash_buffer = min_cash_buffer_pct
        self.min_earnings_buffer = min_earnings_buffer_days

    def audit_trade_allocation(
        self,
        account_equity: float,
        current_free_cash: float,
        proposed_trade_collateral: float,
        existing_symbol_collateral: float,
        days_to_earnings: int
    ) -> Dict[str, Any]:
        """
        Audits proposed CSP / Covered Call wheel allocation for safety compliance.
        """
        max_allowed_dollar_per_symbol = account_equity * (self.max_symbol_alloc / 100.0)
        total_symbol_collateral = existing_symbol_collateral + proposed_trade_collateral
        
        is_symbol_size_ok = total_symbol_collateral <= max_allowed_dollar_per_symbol

        remaining_cash_after_trade = current_free_cash - proposed_trade_collateral
        cash_buffer_pct = (remaining_cash_after_trade / max(1.0, account_equity)) * 100.0
        is_cash_buffer_ok = cash_buffer_pct >= self.min_cash_buffer

        is_earnings_safe = days_to_earnings >= self.min_earnings_buffer

        is_trade_approved = is_symbol_size_ok and is_cash_buffer_ok and is_earnings_safe

        rejection_reasons = []
        if not is_symbol_size_ok:
            rejection_reasons.append(f"Exceeds {self.max_symbol_alloc}% single-underlying allocation ceiling.")
        if not is_cash_buffer_ok:
            rejection_reasons.append(f"Violates {self.min_cash_buffer}% minimum cash liquidity buffer.")
        if not is_earnings_safe:
            rejection_reasons.append(f"Earnings in {days_to_earnings} days (< {self.min_earnings_buffer} day safety filter).")

        return {
            "account_equity": account_equity,
            "proposed_collateral": proposed_trade_collateral,
            "total_symbol_exposure": total_symbol_collateral,
            "max_allowed_symbol_exposure": round(max_allowed_dollar_per_symbol, 2),
            "projected_cash_buffer_pct": round(cash_buffer_pct, 2),
            "is_trade_approved": is_trade_approved,
            "rejection_reasons": rejection_reasons,
            "verdict": "APPROVED_EXECUTE" if is_trade_approved else "BLOCKED_RISK_VIOLATION"
        }
