"""
Module BO1: Asymmetric 1:2 Ratio Backspread and Volatility Breakout Engine
Synthesized from Frank Richmond's 'Options Trading Crash Course'.
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RatioBackspreadState:
    short_strike: float
    long_strike: float
    net_debit_credit: float
    max_loss_point: float
    upper_bep: float
    lower_bep: float
    implied_volatility: float
    ratio_short: int
    ratio_long: int
    is_call_spread: bool

class RatioBackspreadEngine:
    def construct_call_backspread(self, spot: float, atm_strike: float, otm_strike: float, short_prem: float, long_prem: float) -> RatioBackspreadState:
        net_flow = (2.0 * long_prem) - short_prem
        max_loss = (otm_strike - atm_strike) + net_flow
        upper_bep = otm_strike + max_loss
        lower_bep = atm_strike + (net_flow if net_flow < 0 else 0)
        
        return RatioBackspreadState(
            short_strike=atm_strike,
            long_strike=otm_strike,
            net_debit_credit=net_flow,
            max_loss_point=max_loss,
            upper_bep=upper_bep,
            lower_bep=lower_bep,
            implied_volatility=0.30,
            ratio_short=1,
            ratio_long=2,
            is_call_spread=True
        )

    def evaluate_pnl_at_expiry(self, state: RatioBackspreadState, terminal_price: float) -> float:
        if state.is_call_spread:
            short_val = max(0.0, terminal_price - state.short_strike)
            long_val = 2.0 * max(0.0, terminal_price - state.long_strike)
            return (long_val - short_val) - state.net_debit_credit
        else:
            short_val = max(0.0, state.short_strike - terminal_price)
            long_val = 2.0 * max(0.0, state.long_strike - terminal_price)
            return (long_val - short_val) - state.net_debit_credit
