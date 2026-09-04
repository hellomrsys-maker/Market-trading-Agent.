"""
Options Equivalency, Synthetics & Arbitrage Engine (Module AC1 - Python)
Synthesizes the options equivalency principles of Tony Saliba (Managing Expectations):
- P.U.C. Synthetic Matrix & 6 Basic Synthetic Equivalencies
- Basis & Carry Calculation (Basis = Carry - Dividends = S * r * t - Div)
- Put-Call Parity Arbitrage Detector (C - P = S - X + Basis)
- Conversion & Reversal Pricing with Rebate Rates and Dividend Liabilities
- Box Spread 4-Way Decomposition & Synthetic Straddles
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import math


@dataclass
class SyntheticQuote:
    call_bid: float
    call_ask: float
    put_bid: float
    put_ask: float
    stock_price: float
    strike_price: float
    interest_rate: float
    days_to_expiration: int
    dividend_expected: float = 0.0


@dataclass
class ConversionReversalResult:
    strategy_type: str        # "CONVERSION" or "REVERSAL"
    cost_to_carry: float
    dividend_adjustment: float
    theoretical_combo_price: float
    actual_combo_price: float
    arbitrage_edge: float
    is_arbitrage_profitable: bool


class OptionsEquivalencySyntheticsEngine:
    """
    Module AC1: Options Equivalency, Synthetics & Arbitrage Engine.
    Evaluates synthetic positions, calculates forward basis, and detects conversion/reversal arbitrage opportunities.
    """

    def __init__(self):
        pass

    def compute_basis_and_forward(
        self,
        stock_price: float,
        interest_rate: float,
        days_to_exp: int,
        dividend: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculates Carry, Basis and Future Stock Value:
        Carry = Stock Price * Interest Rate * (Days / 360)
        Basis = Carry - Dividends
        Stock Future Value = Stock Price + Basis
        """
        t = days_to_exp / 360.0
        carry = stock_price * interest_rate * t
        basis = carry - dividend
        forward_price = stock_price + basis

        return {
            "carry": round(carry, 4),
            "dividend": round(dividend, 4),
            "basis": round(basis, 4),
            "forward_price": round(forward_price, 4)
        }

    def verify_put_call_parity(self, quote: SyntheticQuote) -> Dict[str, Any]:
        """
        Put-Call Parity: C - P = S - X + Basis
        Evaluates theoretical stock price and synthetic call/put values.
        """
        basis_info = self.compute_basis_and_forward(
            quote.stock_price, quote.interest_rate, quote.days_to_expiration, quote.dividend_expected
        )
        basis = basis_info["basis"]

        call_mid = (quote.call_bid + quote.call_ask) / 2.0
        put_mid = (quote.put_bid + quote.put_ask) / 2.0

        # Theoretical parity stock price S = C - P + X - Basis
        theoretical_stock = call_mid - put_mid + quote.strike_price - basis
        discrepancy = quote.stock_price - theoretical_stock

        # Synthetic call = S - X + P + Basis
        synthetic_call_price = quote.stock_price - quote.strike_price + put_mid + basis
        # Synthetic put = C + X - S - Basis
        synthetic_put_price = call_mid + quote.strike_price - quote.stock_price - basis

        return {
            "actual_stock_price": quote.stock_price,
            "theoretical_stock_price": round(theoretical_stock, 4),
            "parity_discrepancy": round(discrepancy, 4),
            "synthetic_call_price": round(synthetic_call_price, 4),
            "synthetic_put_price": round(synthetic_put_price, 4),
            "better_call_execution": "SYNTHETIC" if synthetic_call_price > call_mid else "NATURAL",
            "better_put_execution": "SYNTHETIC" if synthetic_put_price > put_mid else "NATURAL"
        }

    def evaluate_conversion_reversal(
        self,
        quote: SyntheticQuote,
        borrowing_rate: float = 0.025,
        rebate_rate: float = 0.07
    ) -> Dict[str, ConversionReversalResult]:
        """
        Conversion: Long Stock + Long Put + Short Call (+S + P - C)
        Reversal: Short Stock + Short Put + Long Call (-S - P + C)
        In equities, carry/rebate is calculated on the Strike Price.
        """
        t = quote.days_to_expiration / 360.0
        
        # 1. Conversion: Carry paid on strike
        conv_carry = quote.strike_price * borrowing_rate * t
        conv_cost_basis = quote.stock_price + conv_carry - quote.dividend_expected
        # Call sold at bid, put bought at ask
        conv_actual_combo = quote.strike_price - quote.call_bid + quote.put_ask
        conv_edge = conv_cost_basis - conv_actual_combo
        
        conversion_res = ConversionReversalResult(
            strategy_type="CONVERSION",
            cost_to_carry=round(conv_carry, 4),
            dividend_adjustment=round(quote.dividend_expected, 4),
            theoretical_combo_price=round(conv_cost_basis, 4),
            actual_combo_price=round(conv_actual_combo, 4),
            arbitrage_edge=round(conv_edge, 4),
            is_arbitrage_profitable=conv_edge > 0.05
        )

        # 2. Reversal: Rebate received on strike
        rev_rebate = quote.strike_price * rebate_rate * t
        rev_net_stock = quote.stock_price + (rev_rebate - quote.dividend_expected)
        # Call bought at ask, put sold at bid
        rev_actual_combo = quote.strike_price + quote.call_ask - quote.put_bid
        rev_edge = rev_actual_combo - rev_net_stock

        reversal_res = ConversionReversalResult(
            strategy_type="REVERSAL",
            cost_to_carry=round(rev_rebate, 4),
            dividend_adjustment=round(quote.dividend_expected, 4),
            theoretical_combo_price=round(rev_net_stock, 4),
            actual_combo_price=round(rev_actual_combo, 4),
            arbitrage_edge=round(rev_edge, 4),
            is_arbitrage_profitable=rev_edge > 0.05
        )

        return {
            "conversion": conversion_res,
            "reversal": reversal_res
        }

    def evaluate_box_spread(
        self,
        k1_call_spread_cost: float,
        k1_put_spread_cost: float,
        k1_strike: float,
        k2_strike: float
    ) -> Dict[str, Any]:
        """
        Box Spread = Long Call Vertical + Long Put Vertical = K2 - K1 (at Expiry)
        """
        box_cost = k1_call_spread_cost + k1_put_spread_cost
        box_value_at_expiry = abs(k2_strike - k1_strike)
        guaranteed_profit = box_value_at_expiry - box_cost

        return {
            "k1_strike": k1_strike,
            "k2_strike": k2_strike,
            "box_cost": round(box_cost, 4),
            "box_par_value": round(box_value_at_expiry, 4),
            "guaranteed_profit": round(guaranteed_profit, 4),
            "is_arbitrage": guaranteed_profit > 0.05
        }
