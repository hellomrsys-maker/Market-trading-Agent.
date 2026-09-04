"""
Commodity Physical Delivery Risk, First Notice Day (FND) & Roll Governor Engine (Module AT1 - Python)
Synthesizes Carley Garner's "A Trader's First Book on Commodities":
- First Notice Day (FND) & Last Trading Day (LTD) Automated Roll Countdown
- Cash-Settled vs. Physical Delivery Protocol Differentiation
- Volume-Crossover Liquidity Roll Trigger: Roll front-month when Volume(M2) > Volume(M1)
"""

from typing import Dict, List, Any


class DeliveryRollGovernorEngine:
    PHYSICAL_DELIVERY_SYMBOLS = {"CL", "NG", "ZC", "ZS", "GC", "SI", "HG", "KC", "SB", "CC", "CT", "LE", "HE"}
    CASH_SETTLED_SYMBOLS = {"ES", "NQ", "YM", "RTY", "VIX", "DX"}

    def __init__(self, fnd_warning_days: int = 5):
        self.fnd_warning_days = fnd_warning_days

    def evaluate_delivery_risk(
        self,
        symbol: str,
        days_to_fnd: int,
        days_to_ltd: int,
        front_month_volume: float,
        next_month_volume: float
    ) -> Dict[str, Any]:
        """
        Audits physical delivery risk and issues mandatory roll directives.
        """
        is_physical = symbol.upper() in self.PHYSICAL_DELIVERY_SYMBOLS
        settlement_type = "PHYSICAL_DELIVERY" if is_physical else "CASH_SETTLED"

        # Volume crossover check (liquidity transitioning to back month)
        is_volume_rolled = next_month_volume > front_month_volume

        # Roll triggers
        is_fnd_danger = is_physical and (days_to_fnd <= self.fnd_warning_days)
        is_immediate_close_required = is_physical and (days_to_fnd <= 1)

        action = "HOLD_CURRENT_MONTH"
        if is_immediate_close_required:
            action = "MANDATORY_LIQUIDATE_PHYSICAL_DELIVERY_IMMINENT"
        elif is_fnd_danger or is_volume_rolled:
            action = "EXECUTE_CALENDAR_ROLL_TO_NEXT_MONTH"

        return {
            "symbol": symbol.upper(),
            "settlement_type": settlement_type,
            "days_to_fnd": days_to_fnd,
            "days_to_ltd": days_to_ltd,
            "is_physical_delivery": is_physical,
            "is_volume_rolled": is_volume_rolled,
            "is_fnd_danger": is_fnd_danger,
            "recommended_action": action
        }
