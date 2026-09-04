"""
agent/risk/greeks_aggregator.py
================================
OptionAlpha Agent — Live Greeks & Exposure Aggregator

Calculates aggregated portfolio Greeks (Delta $, Gamma $, Vega $, Theta $/day)
across all open Wheel (CSP/CC) and Iron Condor positions.
"""

from __future__ import annotations

from typing import Dict, List


class GreeksAggregator:
    """
    Aggregates position-level Greeks into portfolio dollar sensitivities.
    """

    @staticmethod
    def aggregate(
        positions: List[Dict],
        current_spots: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Computes portfolio-level dollar Greeks.
        """
        net_delta_dollars = 0.0
        net_gamma_dollars = 0.0
        net_vega_dollars = 0.0
        net_theta_dollars = 0.0

        for pos in positions:
            sym = pos.get("symbol", "")
            spot = current_spots.get(sym, 100.0)
            qty = pos.get("qty", 1)

            # Wheel CSP (Short Put) -> positive delta, negative gamma, positive theta, negative vega
            if pos.get("stage") == "CSP":
                delta = float(pos.get("delta", -0.30))  # delta of put is negative, but short is -1 * delta
                gamma = float(pos.get("gamma", 0.02))
                theta = float(pos.get("theta", 0.05))
                vega = float(pos.get("vega", 0.10))

                net_delta_dollars += (-1.0 * delta) * spot * 100.0 * qty
                net_gamma_dollars += (-1.0 * gamma) * (spot ** 2) * 100.0 * qty
                net_theta_dollars += (theta * 100.0 * qty)
                net_vega_dollars += (-1.0 * vega) * 100.0 * qty

            # Wheel CC (Short Call) -> negative delta, negative gamma, positive theta, negative vega
            elif pos.get("stage") == "CC":
                delta = float(pos.get("delta", 0.20))
                gamma = float(pos.get("gamma", 0.02))
                theta = float(pos.get("theta", 0.05))
                vega = float(pos.get("vega", 0.10))

                net_delta_dollars += (-1.0 * delta) * spot * 100.0 * qty
                net_gamma_dollars += (-1.0 * gamma) * (spot ** 2) * 100.0 * qty
                net_theta_dollars += (theta * 100.0 * qty)
                net_vega_dollars += (-1.0 * vega) * 100.0 * qty

            # Iron Condor (Market Neutral)
            elif "short_put" in pos or "wing_width" in pos:
                net_delta_dollars += 0.0  # Delta neutral
                net_theta_dollars += 0.15 * 100.0 * qty
                net_vega_dollars += -0.20 * 100.0 * qty

        return {
            "net_delta_dollars": round(net_delta_dollars, 2),
            "net_gamma_dollars": round(net_gamma_dollars, 2),
            "net_vega_dollars": round(net_vega_dollars, 2),
            "net_theta_dollars": round(net_theta_dollars, 2),
        }
