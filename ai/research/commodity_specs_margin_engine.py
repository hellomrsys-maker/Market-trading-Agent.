"""
Futures Contract Specifications, Tick Multipliers & SPAN Margin Engine (Module AS1 - Python)
Synthesizes Carley Garner's "A Trader's First Book on Commodities":
- Multi-Exchange Contract Directory (CL, NG, ZC, ZS, GC, ES point values, multipliers, tick increments)
- SPAN Initial vs. Maintenance Margin Buffer & Proximity to Forced Liquidation
- Correlated Spread SPAN Margin Discount Calculator (e.g., Crack/Calendar spreads reducing initial margin)
"""

from typing import Dict, List, Any


class CommoditySpecsMarginEngine:
    # Contract specs: (multiplier, tick_size, tick_value, default_initial_margin, default_maintenance_margin)
    CONTRACT_DIRECTORY = {
        "CL": {"name": "Crude Oil (NYMEX)", "unit": "1,000 barrels", "multiplier": 1000.0, "tick_size": 0.01, "tick_value": 10.00, "initial_margin": 6500.0, "maint_margin": 5900.0},
        "NG": {"name": "Natural Gas (NYMEX)", "unit": "10,000 MMBtu", "multiplier": 10000.0, "tick_size": 0.001, "tick_value": 10.00, "initial_margin": 4200.0, "maint_margin": 3800.0},
        "ZC": {"name": "Corn (CBOT)", "unit": "5,000 bushels", "multiplier": 50.0, "tick_size": 0.25, "tick_value": 12.50, "initial_margin": 1800.0, "maint_margin": 1600.0},
        "ZS": {"name": "Soybeans (CBOT)", "unit": "5,000 bushels", "multiplier": 50.0, "tick_size": 0.25, "tick_value": 12.50, "initial_margin": 3200.0, "maint_margin": 2900.0},
        "GC": {"name": "Gold (COMEX)", "unit": "100 troy oz", "multiplier": 100.0, "tick_size": 0.10, "tick_value": 10.00, "initial_margin": 8500.0, "maint_margin": 7700.0},
        "ES": {"name": "E-mini S&P 500 (CME)", "unit": "$50 x Index", "multiplier": 50.0, "tick_size": 0.25, "tick_value": 12.50, "initial_margin": 12000.0, "maint_margin": 10900.0}
    }

    def __init__(self):
        pass

    def get_contract_specs(self, symbol: str) -> Dict[str, Any]:
        return self.CONTRACT_DIRECTORY.get(symbol.upper(), self.CONTRACT_DIRECTORY["ES"])

    def calculate_dollar_move(self, symbol: str, price_change: float, num_contracts: int = 1) -> float:
        specs = self.get_contract_specs(symbol)
        return price_change * specs["multiplier"] * num_contracts

    def audit_span_margin_health(
        self,
        account_equity: float,
        open_positions: List[Dict[str, Any]],
        spread_discount_factor: float = 0.0
    ) -> Dict[str, Any]:
        """
        open_positions: [{'symbol': 'CL', 'contracts': 2, 'is_spread': False}, ...]
        """
        total_initial_margin = 0.0
        total_maint_margin = 0.0

        for pos in open_positions:
            specs = self.get_contract_specs(pos["symbol"])
            c = pos.get("contracts", 1)
            disc = spread_discount_factor if pos.get("is_spread", False) else 0.0
            
            im = specs["initial_margin"] * (1.0 - disc) * c
            mm = specs["maint_margin"] * (1.0 - disc) * c
            
            total_initial_margin += im
            total_maint_margin += mm

        margin_excess = account_equity - total_maint_margin
        leverage_ratio = (total_initial_margin / max(1.0, account_equity)) * 100.0

        # Proximity score: 1.0 = Safe (equity >= initial), 0.0 = Margin call (equity == maint), <0 = Liquidation
        if total_initial_margin > total_maint_margin:
            proximity = (account_equity - total_maint_margin) / (total_initial_margin - total_maint_margin)
        else:
            proximity = 1.0

        is_margin_call = account_equity < total_maint_margin
        is_safe = proximity >= 1.0

        status = "HEALTHY"
        if is_margin_call:
            status = "FORCED_LIQUIDATION_MARGIN_CALL"
        elif not is_safe:
            status = "WARNING_MARGIN_MAINTENANCE_DANGER"

        return {
            "account_equity": account_equity,
            "total_initial_margin": round(total_initial_margin, 2),
            "total_maint_margin": round(total_maint_margin, 2),
            "margin_excess": round(margin_excess, 2),
            "margin_utilization_pct": round(leverage_ratio, 2),
            "proximity_score": round(proximity, 3),
            "status": status,
            "is_safe": is_safe
        }
