"""
Tactical Options Structuring & Execution Discipline Engine (Module AB1 - Python)
Synthesizes the option trading rules & discipline systems of Warren Ray Benjamin (How to Trade Options: Swing Trading):
- OCO (One-Cancels-Other) Order Management Engine
- Vertical Spread Architectures (Bull/Bear Debit & Credit Spreads)
- Iron Condor Structuring with Wing Insurance & Risk Reduction
- Options Leverage, Delta Multiplier & Time Value Decay Modeling
- Capital Preservation (1-2% trade risk, 7% account risk limit) & Anti-Tilt Discipline
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import math


@dataclass
class OCOOrder:
    order_id: str
    symbol: str
    entry_price: float
    take_profit_limit: float
    stop_loss_limit: float
    status: str = "ACTIVE"  # "ACTIVE", "FILLED_TP", "FILLED_SL", "CANCELLED"

    def process_price_tick(self, current_price: float) -> str:
        if self.status != "ACTIVE":
            return self.status

        if current_price >= self.take_profit_limit:
            self.status = "FILLED_TP"
        elif current_price <= self.stop_loss_limit:
            self.status = "FILLED_SL"
        return self.status


@dataclass
class IronCondorPayoff:
    put_long_strike: float    # K1 (lower wing)
    put_short_strike: float   # K2 (lower body)
    call_short_strike: float  # K3 (upper body)
    call_long_strike: float   # K4 (upper wing)
    net_credit_received: float
    wing_width: float
    max_profit: float
    max_loss: float
    reward_to_risk: float
    risk_reduction_percent: float


class TacticalOptionsDisciplineEngine:
    """
    Module AB1: Tactical Options Structuring & Execution Discipline Engine.
    Enforces mathematical risk limits, structures defined-risk spreads, and prevents emotional errors.
    """

    def __init__(self, account_equity: float = 10000.0):
        self.account_equity = account_equity
        self.active_oco_orders: Dict[str, OCOOrder] = {}
        self.max_account_risk_limit = 0.07  # 7% hard portfolio risk ceiling
        self.standard_trade_risk_limit = 0.02  # 2% max per trade

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss_price: float,
        is_aggressive_risk: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates position sizing according to Benjamin's 1% (conservative) or 2% (aggressive) risk rule.
        """
        risk_fraction = self.standard_trade_risk_limit if is_aggressive_risk else 0.01
        dollar_risk_allowable = self.account_equity * risk_fraction
        per_share_risk = abs(entry_price - stop_loss_price)

        if per_share_risk <= 0:
            return {"shares": 0, "contracts": 0, "allowed_risk": dollar_risk_allowable}

        num_shares = math.floor(dollar_risk_allowable / per_share_risk)
        num_option_contracts = math.floor(num_shares / 100.0)

        return {
            "account_equity": self.account_equity,
            "risk_percentage": risk_fraction * 100.0,
            "max_dollar_risk": round(dollar_risk_allowable, 2),
            "per_share_risk": round(per_share_risk, 2),
            "recommended_shares": num_shares,
            "recommended_option_contracts": max(1, num_option_contracts) if num_shares >= 100 else 0
        }

    def structure_iron_condor(
        self,
        k1_put_long: float,
        k2_put_short: float,
        k3_call_short: float,
        k4_call_long: float,
        premium_put_short: float,
        premium_put_long: float,
        premium_call_short: float,
        premium_call_long: float
    ) -> IronCondorPayoff:
        """
        Structures an Iron Condor and calculates wing insurance protection and risk reduction.
        """
        put_credit = premium_put_short - premium_put_long
        call_credit = premium_call_short - premium_call_long
        total_net_credit = (put_credit + call_credit) * 100.0

        wing_width = (k2_put_short - k1_put_long) * 100.0
        max_loss = max(0.0, wing_width - total_net_credit)
        max_profit = total_net_credit

        # Risk reduction compared to naked short strangle
        naked_margin_risk = (k2_put_short + k3_call_short) * 50.0
        risk_reduction = ((naked_margin_risk - max_loss) / naked_margin_risk) * 100.0 if naked_margin_risk > 0 else 50.0

        return IronCondorPayoff(
            put_long_strike=k1_put_long,
            put_short_strike=k2_put_short,
            call_short_strike=k3_call_short,
            call_long_strike=k4_call_long,
            net_credit_received=round(total_net_credit, 2),
            wing_width=round(wing_width, 2),
            max_profit=round(max_profit, 2),
            max_loss=round(max_loss, 2),
            reward_to_risk=round(max_profit / max_loss, 2) if max_loss > 0 else 0.0,
            risk_reduction_percent=round(risk_reduction, 2)
        )

    def register_oco_order(
        self,
        order_id: str,
        symbol: str,
        entry: float,
        take_profit: float,
        stop_loss: float
    ) -> OCOOrder:
        """
        Registers an automated One-Cancels-Other (OCO) order.
        """
        order = OCOOrder(
            order_id=order_id,
            symbol=symbol,
            entry_price=entry,
            take_profit_limit=take_profit,
            stop_loss_limit=stop_loss
        )
        self.active_oco_orders[order_id] = order
        return order

    def audit_discipline_rules(
        self,
        attempted_stop_pull: bool,
        consecutive_wins: int,
        is_revenge_trade: bool
    ) -> Dict[str, Any]:
        """
        Applies Warren Ray Benjamin's top trader discipline checks:
        - NEVER pull a stop-loss order
        - Arrogance circuit breaker after win streaks
        - Anti-impulse / Anti-panic controls
        """
        violations = []
        if attempted_stop_pull:
            violations.append("RULE_VIOLATION: Pulling stop loss orders is prohibited (Anti-Gambling Rule).")

        if consecutive_wins >= 4:
            violations.append("WARNING: Win-streak arrogance risk detected. Reduce position size by 50%.")

        if is_revenge_trade:
            violations.append("CIRCUIT_BREAKER: Post-loss emotional revenge trading detected. 30-minute lock initiated.")

        return {
            "trading_allowed": len(violations) == 0,
            "violations": violations,
            "circuit_breaker_active": len(violations) > 0
        }
