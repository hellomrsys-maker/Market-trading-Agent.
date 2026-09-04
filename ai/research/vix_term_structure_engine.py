"""
VIX Term Structure, Futures Roll Yield & Volatility ETP Arbitrage Engine (Module AG1 - Python)
Synthesizes Russell Rhoads' "Trading VIX Derivatives":
- VIX Term Structure Fitting (M1 to M8 Futures Curve)
- Contango vs. Backwardation Regime Identification
- Annualized Roll Yield Calculation: (F2 - F1)/F1 * (365 / delta_days)
- VIX Futures Basis & Fair Value Pricing
- VVIX (Volatility of VIX) Spike & Tail-Risk Surge Engine (VVIX > 115)
- Volatility ETP Decay Modeling (UVXY, SVXY, VXX roll drag, convexity drag)
"""

import math
from typing import Dict, List, Any, Tuple


class VixTermStructureEngine:
    def __init__(self, high_vvix_threshold: float = 115.0):
        self.high_vvix_threshold = high_vvix_threshold

    def analyze_term_structure(self, spot_vix: float, futures_curve: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        futures_curve: list of dicts [{'month': 1, 'dte': 15, 'price': 16.2}, ...]
        """
        if not futures_curve:
            return {"regime": "UNKNOWN", "slope": 0.0, "roll_yield_pct": 0.0}

        sorted_curve = sorted(futures_curve, key=lambda x: x.get('dte', 0))
        m1 = sorted_curve[0]
        
        # Spot to M1 Basis
        basis_spot_m1 = m1['price'] - spot_vix
        basis_pct = (basis_spot_m1 / spot_vix) * 100.0 if spot_vix > 0 else 0.0

        # Term structure slope (M1 vs M2 or M1 vs last)
        if len(sorted_curve) > 1:
            m2 = sorted_curve[1]
            slope = m2['price'] - m1['price']
            delta_days = max(1, m2['dte'] - m1['dte'])
            # Roll yield from holding short M1 / long M2 in contango
            roll_yield_pct = ((m2['price'] - m1['price']) / m1['price']) * (365.0 / delta_days) * 100.0
        else:
            slope = m1['price'] - spot_vix
            roll_yield_pct = 0.0

        if slope > 0.15:
            regime = "CONTANGO"
        elif slope < -0.15:
            regime = "BACKWARDATION"
        else:
            regime = "FLAT"

        return {
            "spot_vix": spot_vix,
            "m1_price": m1['price'],
            "basis_spot_m1": round(basis_spot_m1, 4),
            "basis_pct": round(basis_pct, 2),
            "regime": regime,
            "slope": round(slope, 4),
            "roll_yield_pct": round(roll_yield_pct, 2),
            "m1_dte": m1['dte'],
            "curve_points": len(sorted_curve)
        }

    def evaluate_vvix_tail_risk(self, spot_vix: float, spot_vvix: float) -> Dict[str, Any]:
        """
        Evaluates VVIX for volatility acceleration and tail risk.
        VVIX > 115 indicates institutional tail hedging / impending volatility explosion.
        """
        vvix_vix_ratio = spot_vvix / spot_vix if spot_vix > 0 else 0.0
        is_elevated_vvix = spot_vvix >= self.high_vvix_threshold

        if spot_vvix > 130.0:
            tail_risk_state = "CRITICAL_SPIKE_WARNING"
            hedge_action = "BUY_VIX_CALL_SPREADS_OR_DEEP_OTM_PUTS"
        elif is_elevated_vvix:
            tail_risk_state = "HIGH_VOLATILITY_ACCELERATION"
            hedge_action = "REDUCE_SHORT_DELTA_SCALE_LONG_VEGA"
        elif spot_vvix < 80.0:
            tail_risk_state = "COMPLACENCY_TROUGH"
            hedge_action = "CHEAP_VOLATILITY_HARVEST_BUY_LEAPS"
        else:
            tail_risk_state = "NORMAL_REGIME"
            hedge_action = "STANDARD_ALPHA_HARVEST"

        return {
            "spot_vix": spot_vix,
            "spot_vvix": spot_vvix,
            "vvix_vix_ratio": round(vvix_vix_ratio, 3),
            "tail_risk_state": tail_risk_state,
            "hedge_action": hedge_action,
            "is_elevated": is_elevated_vvix
        }

    def calculate_etp_decay(self, etp_symbol: str, leverage: float, contango_roll_yield_annual: float, expense_ratio: float = 0.0095) -> Dict[str, Any]:
        """
        Models decay and drag for products like UVXY (1.5x), SVXY (-0.5x), VXX (1.0x).
        """
        # Daily roll drag approx
        daily_roll_drag = (contango_roll_yield_annual / 365.0) * leverage
        # Annualized compound drag including expense ratio
        estimated_annual_drag_pct = (contango_roll_yield_annual * leverage) + (expense_ratio * 100.0)

        is_shortable_edge = (estimated_annual_drag_pct > 25.0) and (leverage > 0)

        return {
            "symbol": etp_symbol,
            "leverage": leverage,
            "daily_drag_pct": round(daily_roll_drag, 4),
            "annual_drag_pct": round(estimated_annual_drag_pct, 2),
            "shortable_structural_edge": is_shortable_edge,
            "recommendation": "EXPLOIT_STRUCTURAL_ROLL_DECAY" if is_shortable_edge else "AVOID_LONG_BUY_AND_HOLD"
        }
