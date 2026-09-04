"""
Professional Trade Adjustment, Repair & Dynamic Hedging Protocol Engine (Module AZ1 - Python)
Synthesizes Mark Sebastian's "Trading Options for Edge":
- Sebastian 4-Step Professional Decision Tree (Delta Breach -> Time/Extrinsic Check -> Repair vs Cut)
- Vertical Spread Repair (Rolling untested wing into Iron Condor / Iron Butterfly)
- Dynamic Micro-Delta Hedging protocols
"""

from typing import Dict, List, Any


class TradeAdjustmentRepairEngine:
    def __init__(self, delta_breach_threshold: float = 0.35, max_loss_multiple: float = 2.0):
        self.delta_breach = delta_breach_threshold
        self.max_loss_multiple = max_loss_multiple

    def audit_trade_defense(
        self,
        current_trade_pnl: float,
        initial_credit_received: float,
        tested_short_delta: float,
        dte_days: float,
        extrinsic_value_remaining: float
    ) -> Dict[str, Any]:
        """
        Audits an open spread trade under pressure and outputs the exact adjustment protocol.
        """
        is_delta_breached = abs(tested_short_delta) >= self.delta_breach
        max_allowable_loss = initial_credit_received * self.max_loss_multiple
        is_max_loss_hit = current_trade_pnl <= -max_allowable_loss

        action = "HOLD_POSITION_WITHIN_PARAMETERS"
        protocol = "MAINTAIN"

        if is_max_loss_hit:
            action = "CUT_LOSS_IMMEDIATELY_MAX_LOSS_REACHED"
            protocol = "DISCIPLINED_EXIT"
        elif is_delta_breached:
            if dte_days >= 14.0 and extrinsic_value_remaining > 0.30:
                action = "ROLL_UNTESTED_WING_CLOSER_CONVERT_TO_IRON_CONDOR"
                protocol = "COLLECT_CREDIT_AND_WIDEN_BREAKEVEN"
            elif dte_days < 7.0:
                action = "ROLL_ENTIRE_SPREAD_OUT_IN_TIME_OR_CLOSE"
                protocol = "TIME_DECAY_EXHAUSTION"
            else:
                action = "DELTA_HEDGE_WITH_UNDERLYING_SHARES"
                protocol = "DYNAMIC_NEUTRALIZATION"

        return {
            "current_pnl": round(current_trade_pnl, 2),
            "initial_credit": round(initial_credit_received, 2),
            "tested_short_delta": round(tested_short_delta, 2),
            "dte_days": dte_days,
            "is_delta_breached": is_delta_breached,
            "is_max_loss_hit": is_max_loss_hit,
            "recommended_action": action,
            "protocol": protocol
        }
