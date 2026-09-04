"""
Cash-Secured Put (CSP) Ladder & Acquisition Basis Optimizer Engine (Module AO1 - Python)
Synthesizes Will Weiser's "Options Trading For Beginners 2022":
- Systematic Delta-Targeted CSP Strike Selection (0.20 - 0.30 Delta, 70-80% POP)
- Effective Acquisition Basis Calculation: Strike - Premium Received
- Multi-Tier Put Laddering Schedule across staggered expiration weeks
- Annualized Return on Capital (ROC) & Collateral Efficiency Formula: (Premium / (Strike * 100)) * (365 / DTE) * 100
"""

import math
from typing import Dict, List, Any


class CashSecuredPutEngine:
    def __init__(self, target_delta_min: float = 0.20, target_delta_max: float = 0.30):
        self.delta_min = target_delta_min
        self.delta_max = target_delta_max

    def evaluate_csp_opportunity(
        self,
        spot_price: float,
        strike_price: float,
        premium_received: float,
        dte_days: float,
        put_delta: float
    ) -> Dict[str, Any]:
        """
        Evaluates a Cash-Secured Put for yield and acquisition basis.
        """
        effective_cost_basis = strike_price - premium_received
        discount_from_spot_pct = ((spot_price - effective_cost_basis) / spot_price) * 100.0
        
        collateral_required = strike_price * 100.0
        trade_premium_total = premium_received * 100.0
        
        roc_pct = (trade_premium_total / collateral_required) * 100.0
        annualized_roc_pct = roc_pct * (365.0 / max(1.0, dte_days))
        
        pop_estimate = (1.0 - abs(put_delta)) * 100.0
        is_in_sweet_spot = (self.delta_min <= abs(put_delta) <= self.delta_max) and (30.0 <= dte_days <= 45.0)

        return {
            "spot_price": spot_price,
            "strike_price": strike_price,
            "premium_per_share": premium_received,
            "effective_cost_basis": round(effective_cost_basis, 2),
            "discount_from_spot_pct": round(discount_from_spot_pct, 2),
            "collateral_required": round(collateral_required, 2),
            "trade_roc_pct": round(roc_pct, 2),
            "annualized_roc_pct": round(annualized_roc_pct, 2),
            "est_pop_pct": round(pop_estimate, 1),
            "is_optimal_setup": is_in_sweet_spot
        }

    def generate_csp_ladder_schedule(
        self,
        underlying: str,
        spot_price: float,
        total_collateral_budget: float,
        num_tiers: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generates a staggered expiration ladder (e.g. 7, 14, 21, 28 DTE) with conservative descending delta targets.
        """
        ladder = []
        budget_per_tier = total_collateral_budget / num_tiers
        
        for i in range(1, num_tiers + 1):
            dte = i * 7
            strike = round(spot_price * (1.0 - (0.02 * i)), 1)
            est_premium = round(strike * 0.015 * math.sqrt(dte / 30.0), 2)
            collateral = strike * 100.0
            contracts = max(1, int(budget_per_tier / collateral))
            
            ladder.append({
                "tier": i,
                "dte_days": dte,
                "target_strike": strike,
                "est_premium_per_share": est_premium,
                "contracts_to_sell": contracts,
                "allocated_collateral": round(contracts * collateral, 2),
                "target_delta": round(0.30 - (0.03 * i), 2)
            })
            
        return ladder
