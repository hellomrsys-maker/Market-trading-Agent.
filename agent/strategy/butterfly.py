"""
agent/strategy/butterfly.py
============================
OptionAlpha Agent — Iron Butterfly Strategy

Deploys tight Iron Butterflies during extreme IV crush events (e.g. post-earnings):
  - Sells ATM Straddle (1 ATM Call + 1 ATM Put)
  - Buys OTM Strangle Wings ($5 or $10 wide)
  - Produces high credit yield with defined risk bounds
"""

from __future__ import annotations

from typing import Dict, List, Optional


class IronButterflyStrategy:
    """
    High-IV crush Iron Butterfly selector.
    """

    @staticmethod
    def scan_opportunity(
        symbol: str,
        spot: float,
        chain_contracts: List[Dict],
        iv_rank: float,
        wing_width: float = 5.0,
    ) -> Optional[Dict]:
        if iv_rank < 50.0:  # Only deploy in top 50% IV rank
            return None

        # Filter 30 DTE contracts
        c30 = [c for c in chain_contracts if c.get("dte") == 30]
        if not c30:
            return None

        # Find ATM strike
        strikes = sorted(list({c["strike"] for c in c30}))
        atm_strike = min(strikes, key=lambda s: abs(s - spot))

        short_call = next((c for c in c30 if c["is_call"] and c["strike"] == atm_strike), None)
        short_put = next((c for c in c30 if not c["is_call"] and c["strike"] == atm_strike), None)
        long_call = next((c for c in c30 if c["is_call"] and abs(c["strike"] - (atm_strike + wing_width)) < 0.5), None)
        long_put = next((c for c in c30 if not c["is_call"] and abs(c["strike"] - (atm_strike - wing_width)) < 0.5), None)

        if not (short_call and short_put and long_call and long_put):
            return None

        net_credit = round((short_call["bid"] + short_put["bid"]) - (long_call["ask"] + long_put["ask"]), 2)
        if net_credit < wing_width * 0.40:  # Must collect at least 40% of wing width
            return None

        max_loss = round(wing_width - net_credit, 2)

        return {
            "strategy": "IRON_BUTTERFLY",
            "symbol": symbol,
            "atm_strike": atm_strike,
            "wing_width": wing_width,
            "net_credit": net_credit,
            "max_loss": max_loss,
            "dte": 30,
            "expiry": short_call["expiration_date"],
            "target_profit": round(net_credit * 0.50, 2),
        }
