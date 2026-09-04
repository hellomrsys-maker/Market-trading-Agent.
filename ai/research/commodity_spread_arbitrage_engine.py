"""
Intermarket Commodity Processing & Calendar Spread Arbitrage Engine (Module AL1 - Python)
Synthesizes Jack D. Schwager's "A Complete Guide to the Futures Market":
- Cost-of-Carry Model: F(t,T) = S * exp((r + u - y) * (T - t))
- 3:2:1 Energy Crack Spread: 3 CL <-> 2 RBOB Gasoline + 1 Heating Oil
- Soybean Crush Spread Gross Processing Margin (GPM): Meal*0.022 + Oil*0.11 - Soybeans
- Intra-market Calendar Spreads (Contango Full Carry vs Inverted Backwardation)
"""

import math
from typing import Dict, List, Any


class CommoditySpreadArbitrageEngine:
    def __init__(self, risk_free_rate: float = 0.045):
        self.risk_free_rate = risk_free_rate

    def calculate_cost_of_carry_fair_value(
        self,
        spot_price: float,
        storage_rate_annual: float,
        convenience_yield_annual: float,
        time_to_maturity_years: float
    ) -> Dict[str, Any]:
        """
        F(t,T) = S_t * exp((r + u - y) * T)
        """
        net_carry_rate = self.risk_free_rate + storage_rate_annual - convenience_yield_annual
        fair_futures_price = spot_price * math.exp(net_carry_rate * time_to_maturity_years)
        
        market_structure = "CONTANGO_CARRY" if net_carry_rate > 0 else "INVERTED_BACKWARDATION"

        return {
            "spot_price": spot_price,
            "net_carry_rate": round(net_carry_rate, 4),
            "fair_futures_price": round(fair_futures_price, 2),
            "market_structure": market_structure,
            "annualized_carry_pct": round(net_carry_rate * 100.0, 2)
        }

    def compute_energy_321_crack_spread(
        self,
        crude_oil_price_per_barrel: float,
        gasoline_rbob_price_per_gallon: float,
        heating_oil_price_per_gallon: float
    ) -> Dict[str, Any]:
        """
        3:2:1 Crack Spread = (2 * Gasoline * 42 + 1 * HeatingOil * 42 - 3 * CrudeOil) / 3
        """
        gas_barrel = gasoline_rbob_price_per_gallon * 42.0
        ho_barrel = heating_oil_price_per_gallon * 42.0
        product_revenue = (2.0 * gas_barrel) + (1.0 * ho_barrel)
        feedstock_cost = 3.0 * crude_oil_price_per_barrel

        crack_margin_per_barrel = (product_revenue - feedstock_cost) / 3.0

        is_wide_margin = crack_margin_per_barrel >= 25.0
        is_depressed_margin = crack_margin_per_barrel <= 10.0

        trade_signal = "HOLD"
        if is_wide_margin:
            trade_signal = "SELL_CRACK_SPREAD (Short Products, Long Crude)"
        elif is_depressed_margin:
            trade_signal = "BUY_CRACK_SPREAD (Long Products, Short Crude)"

        return {
            "crude_oil_bbl": crude_oil_price_per_barrel,
            "gasoline_gal": gasoline_rbob_price_per_gallon,
            "heating_oil_gal": heating_oil_price_per_gallon,
            "crack_margin_per_barrel": round(crack_margin_per_barrel, 2),
            "signal": trade_signal
        }

    def compute_soybean_crush_spread(
        self,
        soybeans_cents_per_bushel: float,
        soybean_meal_dollars_per_ton: float,
        soybean_oil_cents_per_pound: float
    ) -> Dict[str, Any]:
        """
        Gross Processing Margin (GPM) in cents per bushel:
        GPM = (Meal $/ton * 0.022 * 100) + (Oil cents/lb * 11) - Soybeans cents/bu
        1 bushel = 48 lbs meal (0.024 ton) + 11 lbs oil
        Standard simplified GPM = (Meal * 0.022 * 100) + (Oil * 11) - Soybeans
        """
        meal_revenue_cents = soybean_meal_dollars_per_ton * 2.2
        oil_revenue_cents = soybean_oil_cents_per_pound * 11.0
        total_revenue_cents = meal_revenue_cents + oil_revenue_cents
        gpm_cents_per_bushel = total_revenue_cents - soybeans_cents_per_bushel

        is_high_gpm = gpm_cents_per_bushel > 180.0
        is_low_gpm = gpm_cents_per_bushel < 60.0

        signal = "HOLD"
        if is_high_gpm:
            signal = "ENTER_REVERSE_CRUSH (Sell Products, Buy Beans)"
        elif is_low_gpm:
            signal = "ENTER_CRUSH_SPREAD (Buy Beans, Sell Products)"

        return {
            "soybeans_bu": soybeans_cents_per_bushel,
            "meal_ton": soybean_meal_dollars_per_ton,
            "oil_lb": soybean_oil_cents_per_pound,
            "gpm_cents_per_bushel": round(gpm_cents_per_bushel, 2),
            "gpm_dollars_per_bushel": round(gpm_cents_per_bushel / 100.0, 2),
            "signal": signal
        }
