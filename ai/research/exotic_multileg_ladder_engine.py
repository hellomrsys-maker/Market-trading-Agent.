"""
Module BP1: Exotic Multi-Leg Combinator, Ladder, Strip/Strap and Elasticity Engine
Synthesized from Ryan Bitstone's 'Options Trading Made Clear'.
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ExoticMultiLegLadderState:
    strike_rung1: float
    strike_rung2: float
    strike_rung3: float
    strike_rung4: float
    lambda_elasticity: float
    net_package_premium: float
    max_sweet_spot_profit: float
    strategy_archetype: int
    call_legs_count: int
    put_legs_count: int

class ExoticMultiLegLadderEngine:
    def compute_lambda_elasticity(self, delta: float, spot: float, option_price: float) -> float:
        if option_price <= 0.001:
            return 0.0
        return (delta * spot) / option_price

    def construct_strip(self, spot: float, atm_strike: float, call_prem: float, put_prem: float) -> ExoticMultiLegLadderState:
        # Strip: 2 Puts + 1 Call
        total_prem = (2.0 * put_prem) + call_prem
        delta = (1.0 * 0.50) + (2.0 * (-0.50))
        lam = self.compute_lambda_elasticity(delta, spot, total_prem)
        
        return ExoticMultiLegLadderState(
            strike_rung1=atm_strike,
            strike_rung2=atm_strike,
            strike_rung3=atm_strike,
            strike_rung4=0.0,
            lambda_elasticity=lam,
            net_package_premium=total_prem,
            max_sweet_spot_profit=999999.0,
            strategy_archetype=1,
            call_legs_count=1,
            put_legs_count=2
        )

    def construct_strap(self, spot: float, atm_strike: float, call_prem: float, put_prem: float) -> ExoticMultiLegLadderState:
        # Strap: 2 Calls + 1 Put
        total_prem = (2.0 * call_prem) + put_prem
        delta = (2.0 * 0.50) + (1.0 * (-0.50))
        lam = self.compute_lambda_elasticity(delta, spot, total_prem)
        
        return ExoticMultiLegLadderState(
            strike_rung1=atm_strike,
            strike_rung2=atm_strike,
            strike_rung3=atm_strike,
            strike_rung4=0.0,
            lambda_elasticity=lam,
            net_package_premium=total_prem,
            max_sweet_spot_profit=999999.0,
            strategy_archetype=2,
            call_legs_count=2,
            put_legs_count=1
        )
