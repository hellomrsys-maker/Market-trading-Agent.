"""
agent/risk/stress_tester.py
============================
OptionAlpha Agent — Macro Scenario Stress Testing Engine

Evaluates CCAR-inspired severe market shock scenarios on the active portfolio:
  1. Flash Crash: -10% spot drop, VIX spike +20 pts
  2. Volatility Crush: -30% IV drop overnight
  3. Gap Up Rally: +8% underlying surge (Short Call squeeze)
  4. Liquidity Crisis: 5x bid-ask spread blowout
"""

from __future__ import annotations

from typing import Dict, List


class MacroStressTester:
    """
    Simulates severe macroeconomic shocks on active option positions.
    """

    @staticmethod
    def run_stress_tests(
        equity: float,
        net_delta_dollars: float,
        net_gamma_dollars: float,
        net_vega_dollars: float,
        net_theta_dollars: float,
        num_open_contracts: int = 4,
    ) -> Dict[str, Dict]:
        """
        Calculates P&L impact across 4 stress scenarios.
        """
        results = {}

        # ── Scenario 1: Flash Crash (-10% spot, +20 pts IV spike) ─
        spot_shock_1 = -0.10
        vol_shock_1 = 20.0
        pnl_1 = (net_delta_dollars * spot_shock_1) + \
                (0.5 * net_gamma_dollars * (spot_shock_1 ** 2)) + \
                (net_vega_dollars * vol_shock_1)
        results["Flash_Crash_Minus_10Pct"] = {
            "pnl_impact_dollars": round(pnl_1, 2),
            "pnl_pct_of_equity": round((pnl_1 / equity) * 100.0, 2),
            "passes_stress_test": (pnl_1 / equity) >= -0.05,  # Max -5% equity loss allowed
        }

        # ── Scenario 2: Volatility Crush (-30% relative IV drop) ──
        vol_shock_2 = -10.0  # -10 vol points
        pnl_2 = net_vega_dollars * vol_shock_2 + net_theta_dollars * 1.0
        results["Volatility_Crush_Minus_30Pct"] = {
            "pnl_impact_dollars": round(pnl_2, 2),
            "pnl_pct_of_equity": round((pnl_2 / equity) * 100.0, 2),
            "passes_stress_test": (pnl_2 / equity) >= -0.05,
        }

        # ── Scenario 3: Gap Up Rally (+8% spot jump) ──────────────
        spot_shock_3 = 0.08
        pnl_3 = (net_delta_dollars * spot_shock_3) + (0.5 * net_gamma_dollars * (spot_shock_3 ** 2))
        results["Gap_Up_Rally_Plus_8Pct"] = {
            "pnl_impact_dollars": round(pnl_3, 2),
            "pnl_pct_of_equity": round((pnl_3 / equity) * 100.0, 2),
            "passes_stress_test": (pnl_3 / equity) >= -0.05,
        }

        # ── Scenario 4: Liquidity Crisis (5x spread expansion) ────
        spread_slippage = num_open_contracts * 100.0 * 0.40  # $0.40 extra slippage per contract
        pnl_4 = -spread_slippage
        results["Liquidity_Crisis_Spread_Blowout"] = {
            "pnl_impact_dollars": round(pnl_4, 2),
            "pnl_pct_of_equity": round((pnl_4 / equity) * 100.0, 2),
            "passes_stress_test": True,
        }

        all_pass = all(s["passes_stress_test"] for s in results.values())
        return {
            "overall_stress_pass": all_pass,
            "scenarios": results,
        }
