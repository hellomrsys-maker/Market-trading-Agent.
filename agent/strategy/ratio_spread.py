"""
agent/strategy/ratio_spread.py
===============================
OptionAlpha Agent — Put Ratio Spread (1x2) Strategy

Deploys 1x2 Put Ratio Spreads during mild bearish / neutral regimes:
  - Buys 1 near-the-money Put (Delta ~ -0.40)
  - Sells 2 further out-of-the-money Puts (Delta ~ -0.20)
  - Entered for zero cost or a small net credit
"""

from __future__ import annotations

from typing import Dict, List, Optional


class PutRatioSpreadStrategy:
    """
    1x2 Put Ratio Spread selector.
    """

    @staticmethod
    def scan_opportunity(
        symbol: str,
        spot: float,
        chain_contracts: List[Dict],
        momentum_20d: float,
    ) -> Optional[Dict]:
        # Only deploy when momentum is flat or mildly negative
        if momentum_20d > 0.03 or momentum_20d < -0.10:
            return None

        c45 = [c for c in chain_contracts if not c.get("is_call") and c.get("dte") == 45]
        if not c45:
            return None

        # Long Put (Delta ~ -0.40) & Short Puts (Delta ~ -0.20)
        long_candidates = sorted([p for p in c45 if -0.60 <= p.get("delta", 0) <= -0.25], key=lambda x: x["strike"], reverse=True)
        short_candidates = sorted([p for p in c45 if -0.35 <= p.get("delta", 0) <= -0.05], key=lambda x: x["strike"])

        if not long_candidates or not short_candidates:
            return None

        lp, sp = None, None
        for l in long_candidates:
            for s in short_candidates:
                if l["strike"] > s["strike"]:
                    lp = l
                    sp = s
                    break
            if lp is not None:
                break

        if lp is None or sp is None:
            return None

        # 1x Long Ask vs 2x Short Bid
        net_credit = round((2.0 * sp["bid"]) - lp["ask"], 2)

        max_profit = round((lp["strike"] - sp["strike"]) + net_credit, 2)
        breakeven = round(sp["strike"] - max_profit, 2)

        return {
            "strategy": "PUT_RATIO_SPREAD_1X2",
            "symbol": symbol,
            "long_strike": lp["strike"],
            "short_strike": sp["strike"],
            "net_credit_debit": net_credit,
            "max_profit": max_profit,
            "breakeven": breakeven,
            "dte": 45,
            "expiry": lp["expiration_date"],
        }
