"""
Karl Domm All-Weather Options Portfolio & Tail Risk Vomma Engine (Module BE1 - Python)
Synthesizes Karl Domm's "A Portfolio for All Markets":
- SPAN / Portfolio Margin Stress Testing (-12% slice, -20% slice / 2, +10% slice)
- 4 Market Type Regimes (Rising Bull, Sideways, Grind-Down, Crash)
- Negative VOMMA Mitigation via Long 5-Delta "Teenie" Out-of-the-Money Puts
- Return on Planned Capital vs Return on Margin (<= 65% peak margin rule)
"""

from typing import Dict, List, Any


class AllWeatherVommaEngine:
    def __init__(self, max_margin_utilization_pct: float = 65.0):
        self.max_margin_util = max_margin_utilization_pct

    def classify_market_regime(
        self,
        spx_return_pct: float,
        vix_spike_pts: float,
        is_grind_down: bool = False
    ) -> Dict[str, Any]:
        """
        Classifies market into 1 of 4 Karl Domm regimes:
        1. Rising Bull: SPX > 0, VIX low
        2. Sideways: SPX within +-4%, VIX tame
        3. Grind-Down: Market down, VIX spike < 30 pts
        4. Crash: Fast drop, VIX spike >= 35 pts in 3-5 days
        """
        if vix_spike_pts >= 35.0:
            regime = "CRASH_MARKET"
            hedging_status = "POSITIVE_VOMMA_EXPLOSION"
        elif is_grind_down or (spx_return_pct < -8.0 and vix_spike_pts < 30.0):
            regime = "GRIND_DOWN_MARKET"
            hedging_status = "INTERMEDIATE_DELTA_DEFENSE"
        elif abs(spx_return_pct) <= 4.0:
            regime = "SIDEWAYS_MARKET"
            hedging_status = "MAX_THETA_DECAY_EXTRACTION"
        else:
            regime = "RISING_BULL_MARKET"
            hedging_status = "STEADY_UPSIDE_CAPITAL_PRESERVATION"

        return {
            "spx_return_pct": spx_return_pct,
            "vix_spike_pts": vix_spike_pts,
            "regime": regime,
            "hedging_status": hedging_status
        }

    def calculate_portfolio_margin_requirement(
        self,
        pnl_down_12pct: float,
        pnl_down_20pct: float,
        pnl_up_10pct: float,
        planned_capital: float
    ) -> Dict[str, Any]:
        """
        Thinkorswim / SPAN margin slice calculation:
        Worst case of: (-12% slice, -20% slice / 2, +10% slice).
        """
        slice_12_down = abs(min(0.0, pnl_down_12pct))
        slice_20_down = abs(min(0.0, pnl_down_20pct)) / 2.0
        slice_10_up = abs(min(0.0, pnl_up_10pct))

        margin_requirement = max(slice_12_down, slice_20_down, slice_10_up)
        margin_utilization_pct = (margin_requirement / max(1.0, planned_capital)) * 100.0
        is_safe = margin_utilization_pct <= self.max_margin_util

        return {
            "slice_12_down": round(slice_12_down, 2),
            "slice_20_down_half": round(slice_20_down, 2),
            "slice_10_up": round(slice_10_up, 2),
            "worst_case_margin_requirement": round(margin_requirement, 2),
            "planned_capital": planned_capital,
            "margin_utilization_pct": round(margin_utilization_pct, 2),
            "is_capital_sufficient": is_safe,
            "verdict": "APPROVED_SAFE_MARGIN" if is_safe else "BLOCKED_EXCESSIVE_LEVERAGE"
        }

    def evaluate_teenie_vomma_hedge(
        self,
        core_iron_condor_vomma: float,  # Negative vomma from short options
        num_teenie_puts: int,
        teenie_put_vomma_per_contract: float = 0.08
    ) -> Dict[str, Any]:
        """
        Calculates net portfolio vomma after adding long 5-Delta OTM "teenie" puts.
        """
        hedge_vomma = num_teenie_puts * teenie_put_vomma_per_contract
        net_portfolio_vomma = core_iron_condor_vomma + hedge_vomma
        has_positive_vomma = net_portfolio_vomma > 0.0

        return {
            "core_vomma": core_iron_condor_vomma,
            "teenie_hedge_vomma": round(hedge_vomma, 4),
            "net_portfolio_vomma": round(net_portfolio_vomma, 4),
            "has_positive_vomma": has_positive_vomma,
            "protection_status": "CONVEX_CRASH_PROTECTED" if has_positive_vomma else "VULNERABLE_NEGATIVE_VOMMA"
        }
