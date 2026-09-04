"""
agent/strategy/calendar_spread.py
==================================
OptionAlpha Agent — Diagonal Calendar Spread Strategy

Enters diagonal calendar spreads when the term structure is in backwardation (front IV > back IV):
  - Sells near-term (21 DTE) option to harvest rapid theta decay
  - Buys longer-term (45-60 DTE) option as a hedge
  - Takes profit when spread expands by 50%
"""

from __future__ import annotations

from typing import Dict, List, Optional
from loguru import logger


class CalendarSpreadStrategy:
    """
    Term-structure volatility arbitrage strategy.
    """

    @staticmethod
    def scan_opportunity(
        symbol: str,
        spot: float,
        chain_contracts: List[Dict],
        term_spread: float,  # front IV - back IV
    ) -> Optional[Dict]:
        """
        Evaluates whether a calendar spread meets entry conditions.
        """
        # Require front month IV to be higher than back month (backwardation)
        if term_spread < 0.02:
            return None

        # Find 21 DTE short call and 45 DTE long call at near-ATM strikes
        short_calls = [c for c in chain_contracts if c.get("is_call") and c.get("dte") == 21 and abs(c.get("strike", 0) - spot) / spot < 0.03]
        long_calls = [c for c in chain_contracts if c.get("is_call") and c.get("dte") == 45 and abs(c.get("strike", 0) - spot) / spot < 0.03]

        if not short_calls or not long_calls:
            return None

        sc = short_calls[0]
        lc = long_calls[0]
        debit = round(lc.get("ask", 0) - sc.get("bid", 0), 2)

        if debit <= 0 or debit > spot * 0.05:
            return None

        return {
            "strategy": "CALENDAR_SPREAD",
            "symbol": symbol,
            "strike": sc["strike"],
            "short_expiry": sc["expiration_date"],
            "long_expiry": lc["expiration_date"],
            "short_dte": sc["dte"],
            "long_dte": lc["dte"],
            "net_debit": debit,
            "target_profit": round(debit * 0.50, 2),
            "max_loss": debit,
        }
