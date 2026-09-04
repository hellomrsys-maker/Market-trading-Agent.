"""
Module BJ1: 10-Archetype Institutional Iron Condor & Stochastic Calculus Engine
Synthesized from Vincent Bisette & Hayden Van Der Post's 'Options Master: Strategies to Win'.
"""

import math
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class IronCondorArchetype:
    name: str
    target_dte: int
    target_delta: float
    target_profit_pct: float
    volatility_regime: str
    hedge_protocol: str

class InstitutionalIronCondorEngine:
    ARCHETYPES = {
        1: IronCondorArchetype("Market Stabilizer", 30, 0.16, 50.0, "LOW_MODERATE", "WingAdjustment"),
        2: IronCondorArchetype("Earnings Play", 3, 0.12, 75.0, "HIGH_IV_CRUSH", "ImmediateCloseAtOpen"),
        3: IronCondorArchetype("Index Balancer", 30, 0.20, 50.0, "EQUILIBRIUM", "RollUntestedSide"),
        4: IronCondorArchetype("Monthly Income", 40, 0.15, 50.0, "NORMAL", "SystematicMonthlyRoll"),
        5: IronCondorArchetype("High Volatility Harness", 45, 0.10, 50.0, "HIGH_VIX", "WidenStrikesDeltaDefense"),
        6: IronCondorArchetype("Sector Speculator", 30, 0.18, 50.0, "SECTOR_RANGE", "SupportResistanceAnchored"),
        7: IronCondorArchetype("Diversified Approach", 45, 0.15, 50.0, "UNCORRELATED", "5PctPortfolioBucket"),
        8: IronCondorArchetype("Gamma Guard", 15, 0.25, 40.0, "LOW_VOLATILITY", "MonetizeAcceleratedTheta"),
        9: IronCondorArchetype("Trend Follower", 35, 0.15, 50.0, "POST_TREND_RANGE", "AlignWithRangePivots"),
        10: IronCondorArchetype("Patient Player", 75, 0.12, 60.0, "LONG_TERM_NEUTRAL", "SlowThetaHarvesting")
    }

    def select_archetype(
        self,
        is_earnings_near: bool,
        is_index: bool,
        vix_level: float,
        days_preference: int = 30
    ) -> IronCondorArchetype:
        if is_earnings_near:
            return self.ARCHETYPES[2]
        if is_index and vix_level < 20.0:
            return self.ARCHETYPES[3]
        if vix_level >= 25.0:
            return self.ARCHETYPES[5]
        if days_preference <= 15:
            return self.ARCHETYPES[8]
        if days_preference >= 60:
            return self.ARCHETYPES[10]
        return self.ARCHETYPES[4]

    def solve_geometric_brownian_motion(
        self,
        spot: float,
        drift_mu: float,
        sigma: float,
        time_years: float
    ) -> Dict[str, float]:
        expected_price = spot * math.exp(drift_mu * time_years)
        drift_variance_adjusted = (drift_mu - 0.5 * (sigma ** 2)) * time_years
        return {
            "initial_spot": spot,
            "drift_mu": drift_mu,
            "sigma": sigma,
            "time_years": time_years,
            "expected_price": round(expected_price, 4),
            "drift_variance_adjusted": round(drift_variance_adjusted, 4)
        }

    def verify_martingale_property(self, expected_future_value: float, current_value: float, tolerance: float = 0.001) -> bool:
        return abs(expected_future_value - current_value) <= tolerance

    def calculate_iron_condor_metrics(
        self,
        spot: float,
        put_long: float,
        put_short: float,
        call_short: float,
        call_long: float,
        net_credit: float
    ) -> Dict[str, Any]:
        wing_width = min(put_short - put_long, call_long - call_short)
        max_loss = wing_width - net_credit
        roi_potential_pct = (net_credit / max(0.01, max_loss)) * 100.0
        lower_breakeven = put_short - net_credit
        upper_breakeven = call_short + net_credit

        return {
            "spot": spot,
            "wing_width": round(wing_width, 2),
            "net_credit": round(net_credit, 2),
            "max_loss": round(max_loss, 2),
            "roi_potential_pct": round(roi_potential_pct, 2),
            "lower_breakeven": round(lower_breakeven, 2),
            "upper_breakeven": round(upper_breakeven, 2)
        }