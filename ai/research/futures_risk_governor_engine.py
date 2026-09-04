"""
Schwager Algorithmic Risk Budgeting & Robust System Optimization Engine (Module AN1 - Python)
Synthesizes Jack D. Schwager's "A Complete Guide to the Futures Market":
- Walk-Forward Robustness Degradation Index: Out-of-Sample / In-Sample Sharpe >= 0.65
- Volatility-Scaled ATR Position Sizing: Contracts = (Account * RiskPct) / (ATR * Multiplier * PointVal)
- Maximum Single Trade Risk (1.5%) and Total Portfolio Heat (6.0%) Governance
"""

import math
from typing import Dict, List, Any


class FuturesRiskGovernorEngine:
    def __init__(
        self,
        max_single_trade_risk_pct: float = 1.5,
        max_portfolio_heat_pct: float = 6.0,
        min_robustness_ratio: float = 0.65
    ):
        self.max_trade_risk = max_single_trade_risk_pct
        self.max_heat = max_portfolio_heat_pct
        self.min_robustness = min_robustness_ratio

    def calculate_atr_position_size(
        self,
        account_equity: float,
        risk_pct: float,
        atr_value: float,
        atr_stop_multiplier: float,
        point_value: float
    ) -> Dict[str, Any]:
        """
        Contracts = floor((Account * RiskPct) / (ATR * Multiplier * PointValue))
        """
        clamped_risk_pct = min(risk_pct, self.max_trade_risk) / 100.0
        dollar_risk_target = account_equity * clamped_risk_pct
        
        per_contract_risk = max(1.0, atr_value * atr_stop_multiplier * point_value)
        num_contracts = math.floor(dollar_risk_target / per_contract_risk)

        return {
            "account_equity": account_equity,
            "risk_pct_allocated": round(clamped_risk_pct * 100.0, 2),
            "dollar_risk_target": round(dollar_risk_target, 2),
            "per_contract_risk": round(per_contract_risk, 2),
            "recommended_contracts": max(1, int(num_contracts))
        }

    def evaluate_walk_forward_robustness(
        self,
        in_sample_sharpe: float,
        out_of_sample_sharpe: float
    ) -> Dict[str, Any]:
        """
        Robustness Ratio = OOS_Sharpe / IS_Sharpe
        Must be >= 0.65 to ensure system is not overfitted.
        """
        is_sharpe = max(1e-4, in_sample_sharpe)
        ratio = out_of_sample_sharpe / is_sharpe
        is_robust = (ratio >= self.min_robustness) and (out_of_sample_sharpe > 0.5)

        verdict = "ROBUST_DEPLOYABLE" if is_robust else "OVERFITTED_CURVE_FIT_WARNING"

        return {
            "in_sample_sharpe": round(in_sample_sharpe, 2),
            "out_of_sample_sharpe": round(out_of_sample_sharpe, 2),
            "robustness_ratio": round(ratio, 3),
            "min_required_ratio": self.min_robustness,
            "verdict": verdict,
            "is_deployable": is_robust
        }

    def audit_portfolio_heat(self, open_positions_risk_dollars: List[float], account_equity: float) -> Dict[str, Any]:
        """
        Total heat = sum(open_risk) / account_equity
        Must not exceed max_portfolio_heat_pct (6.0%)
        """
        total_open_risk = sum(open_positions_risk_dollars)
        heat_pct = (total_open_risk / max(1.0, account_equity)) * 100.0
        is_heat_safe = heat_pct <= self.max_heat

        return {
            "total_open_risk_dollars": round(total_open_risk, 2),
            "current_heat_pct": round(heat_pct, 2),
            "max_allowed_heat_pct": self.max_heat,
            "is_heat_compliant": is_heat_safe,
            "action": "PERMIT_NEW_TRADES" if is_heat_safe else "REDUCE_EXPOSURE_BLOCK_NEW_ENTRIES"
        }
