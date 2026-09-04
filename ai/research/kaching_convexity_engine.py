"""
Module BM1: Weekly Cash KaChing and Double-Dip Dynamic Convexity Engine
Synthesized from T. R. Lawrence's 'Options Trading: How to Turn Every Friday into Payday Using Weekly Options'.
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class KaChingConvexityState:
    long_put_strike: float
    short_put_strike: float
    long_put_delta: float
    short_put_delta: float
    net_weekly_premium: float
    cumulative_cash_collected: float
    days_to_earnings: int
    roll_count: int
    double_dip_active: bool
    is_supersized: bool
    status_flags: int

class KaChingConvexityEngine:
    def __init__(self, risk_limit_pct: float = 0.03):
        self.risk_limit_pct = risk_limit_pct

    def initialize_kaching(self, spot_price: float, iv: float, days_to_earnings: int) -> KaChingConvexityState:
        long_delta = 0.38 if iv > 0.35 else 0.25
        long_strike = round(spot_price * (1.0 - (0.08 if long_delta == 0.25 else 0.05)), 2)
        short_delta = 0.50 if spot_price >= long_strike else 0.40
        short_strike = round(spot_price, 2)
        initial_premium = round(spot_price * 0.018 * (1.0 + iv), 2)
        
        return KaChingConvexityState(
            long_put_strike=long_strike,
            short_put_strike=short_strike,
            long_put_delta=long_delta,
            short_put_delta=short_delta,
            net_weekly_premium=initial_premium,
            cumulative_cash_collected=initial_premium,
            days_to_earnings=days_to_earnings,
            roll_count=0,
            double_dip_active=False,
            is_supersized=False,
            status_flags=1
        )

    def evaluate_weekly_harvest(self, state: KaChingConvexityState, current_short_premium: float, day_of_week: int) -> Dict[str, Any]:
        premium_banked_pct = 1.0 - (current_short_premium / max(0.01, state.net_weekly_premium))
        can_double_dip = (premium_banked_pct >= 0.80 and day_of_week in [1, 2, 3])
        need_roll_down = (current_short_premium > 2.0 * state.net_weekly_premium and day_of_week >= 3)
        
        decision = 'HOLD'
        action_data = {}
        if can_double_dip:
            decision = 'DOUBLE_DIP_HARVEST'
            state.double_dip_active = True
            extra_premium = round(state.net_weekly_premium * 0.60, 2)
            state.cumulative_cash_collected += extra_premium
            action_data['extra_cash'] = extra_premium
            action_data['reason'] = f'{premium_banked_pct*100:.1f}% banked early'
        elif need_roll_down:
            decision = 'ROLL_DOWN_DEFENSE'
            state.roll_count += 1
            state.short_put_strike -= 2.0
            roll_credit = round(state.net_weekly_premium * 1.15, 2)
            state.cumulative_cash_collected += (roll_credit - current_short_premium)
            action_data['rolled_strike'] = state.short_put_strike
            action_data['roll_net_credit'] = roll_credit
        elif day_of_week == 5:
            decision = 'EXPIRE_AND_RENEW'
            state.cumulative_cash_collected += state.net_weekly_premium
            state.double_dip_active = False

        return {'decision': decision, 'state': state, 'action_data': action_data}
