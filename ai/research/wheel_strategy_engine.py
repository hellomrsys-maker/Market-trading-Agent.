"""
The Wheel Strategy Lifecycle & Dynamic State Machine Engine (Module AQ1 - Python)
Synthesizes Will Weiser's "Options Trading For Beginners 2022":
- 4-State Lifecycle Governor (Cash -> Short Put -> Shares Assigned -> Covered Call -> Called Away)
- True Net Cost-Basis Amortization Tracker: Purchase Price - Sum(Puts) - Sum(Calls) - Sum(Dividends)
- 50% Max Profit Target Early Exit & Dynamic Roll Rules
"""

from typing import Dict, List, Any


class WheelStrategyEngine:
    def __init__(self):
        pass

    def track_wheel_lifecycle(
        self,
        current_state: str,
        spot_price: float,
        cost_basis_shares: float,
        accumulated_put_premiums: float,
        accumulated_call_premiums: float,
        accumulated_dividends: float,
        active_option_strike: float,
        active_option_original_premium: float,
        active_option_current_price: float
    ) -> Dict[str, Any]:
        """
        States:
        1. STATE_1_LIQUID_CASH (Sell CSP)
        2. STATE_2_PUT_ACTIVE (Monitor 50% profit or roll)
        3. STATE_3_STOCK_ASSIGNED (Own shares, prepare CC)
        4. STATE_4_CALL_ACTIVE (Monitor call exercise or roll)
        """
        # True amortized cost basis per share
        true_net_cost_basis = cost_basis_shares - accumulated_put_premiums - accumulated_call_premiums - accumulated_dividends
        
        # Check 50% profit target on active option
        profit_captured = active_option_original_premium - active_option_current_price
        profit_pct = (profit_captured / max(1e-4, active_option_original_premium)) * 100.0 if active_option_original_premium > 0 else 0.0
        is_50pct_target_hit = profit_pct >= 50.0

        next_action = "MAINTAIN_POSITION"
        next_state = current_state

        if current_state == "STATE_1_LIQUID_CASH":
            next_action = "SCAN_AND_SELL_CSP_30DTE"
            next_state = "STATE_2_PUT_ACTIVE"
        elif current_state == "STATE_2_PUT_ACTIVE":
            if is_50pct_target_hit:
                next_action = "CLOSE_PUT_50PCT_PROFIT_REENTER"
                next_state = "STATE_1_LIQUID_CASH"
            elif spot_price < active_option_strike:
                next_action = "PREPARE_FOR_ASSIGNMENT_OR_ROLL_DOWN_OUT"
                next_state = "STATE_3_STOCK_ASSIGNED"
        elif current_state == "STATE_3_STOCK_ASSIGNED":
            next_action = "SELL_COVERED_CALL_ABOVE_TRUE_NET_BASIS"
            next_state = "STATE_4_CALL_ACTIVE"
        elif current_state == "STATE_4_CALL_ACTIVE":
            if is_50pct_target_hit:
                next_action = "CLOSE_CALL_50PCT_PROFIT_SELL_NEW_CALL"
                next_state = "STATE_3_STOCK_ASSIGNED"
            elif spot_price > active_option_strike:
                next_action = "SHARES_CALLED_AWAY_RETURN_TO_CASH"
                next_state = "STATE_1_LIQUID_CASH"

        return {
            "current_state": current_state,
            "next_state": next_state,
            "true_net_cost_basis": round(true_net_cost_basis, 2),
            "spot_price": spot_price,
            "profit_captured_pct": round(profit_pct, 1),
            "is_50pct_profit_target_hit": is_50pct_target_hit,
            "recommended_action": next_action
        }
