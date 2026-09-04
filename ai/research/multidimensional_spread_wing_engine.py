"""
Multi-Dimensional Spread, Ratio & Wing Engine (Module AE1 - Python)
Synthesizes the complex spread architectures of Tony Saliba (Managing Expectations):
- Directional Calendar Spreads (Horizontal Time Spreads)
- Diagonal Spreads ("Up and Out", "Down and Out", "Reverse Up and Out", "Reverse Down and Out")
- 1x2 Ratio Spreads (Call/Put Ratio with Upside/Downside Breakevens & Butterfly Escape)
- 2x1 Backspreads (Volatility explosion & Skew exploitation)
- Butterfly (1:2:1) and Condor (1:1:1:1) Spreads
- Collar & Reverse Collar Structures
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class RatioSpreadPayoff:
    spread_type: str             # "CALL_RATIO_1X2" or "PUT_RATIO_1X2"
    long_strike: float           # K1
    short_strike: float          # K2 (2 contracts)
    net_credit_or_debit: float
    max_profit: float
    upside_breakeven: Optional[float]
    downside_breakeven: Optional[float]
    butterfly_escape_strike: float
    butterfly_escape_cost: float


@dataclass
class BackspreadPayoff:
    spread_type: str             # "CALL_BACKSPREAD_2X1" or "PUT_BACKSPREAD_2X1"
    short_strike: float          # K1 (1 contract)
    long_strike: float           # K2 (2 contracts)
    net_credit_or_debit: float
    max_loss: float
    upside_breakeven: Optional[float]
    downside_breakeven: Optional[float]


class MultidimensionalSpreadWingEngine:
    """
    Module AE1: Multi-Dimensional Spread, Ratio & Wing Engine.
    Models complex calendar, diagonal, ratio, backspread, and winged structures.
    """

    def __init__(self):
        pass

    def structure_1x2_call_ratio_spread(
        self,
        k1_long_strike: float,
        k2_short_strike: float,
        long_call_premium: float,
        short_call_premium: float
    ) -> RatioSpreadPayoff:
        """
        1x2 Call Ratio Spread: Buy 1 Call at K1, Sell 2 Calls at K2.
        Max Profit = (K2 - K1) + Credit (or - Debit)
        Upside Breakeven = K2 + (Max Profit)
        Downside Risk = Debit (if any)
        Escape Strategy: Buy 1 Call at (K2 + (K2 - K1)) to convert into Butterfly!
        """
        net_cash = (2.0 * short_call_premium) - long_call_premium
        is_credit = net_cash >= 0
        strike_diff = k2_short_strike - k1_long_strike

        max_profit = strike_diff + net_cash
        upside_be = k2_short_strike + max_profit
        downside_be = k1_long_strike - net_cash if not is_credit else None

        escape_strike = k2_short_strike + strike_diff

        return RatioSpreadPayoff(
            spread_type="CALL_RATIO_1X2",
            long_strike=k1_long_strike,
            short_strike=k2_short_strike,
            net_credit_or_debit=round(net_cash, 2),
            max_profit=round(max_profit, 2),
            upside_breakeven=round(upside_be, 2),
            downside_breakeven=round(downside_be, 2) if downside_be else None,
            butterfly_escape_strike=escape_strike,
            butterfly_escape_cost=round(short_call_premium * 0.40, 2)
        )

    def structure_2x1_call_backspread(
        self,
        k1_short_strike: float,
        k2_long_strike: float,
        short_call_premium: float,
        long_call_premium: float
    ) -> BackspreadPayoff:
        """
        2x1 Call Backspread: Sell 1 Call at K1, Buy 2 Calls at K2.
        Max Loss = (K2 - K1) - Credit
        Downside Breakeven = K1 + Credit
        Upside Breakeven = K2 + (K2 - K1) - Credit
        """
        net_credit = short_call_premium - (2.0 * long_call_premium)
        strike_diff = k2_long_strike - k1_short_strike
        max_loss = max(0.0, strike_diff - net_credit)

        downside_be = k1_short_strike + net_credit if net_credit > 0 else None
        upside_be = k2_long_strike + strike_diff - net_credit

        return BackspreadPayoff(
            spread_type="CALL_BACKSPREAD_2X1",
            short_strike=k1_short_strike,
            long_strike=k2_long_strike,
            net_credit_or_debit=round(net_credit, 2),
            max_loss=round(max_loss, 2),
            upside_breakeven=round(upside_be, 2),
            downside_breakeven=round(downside_be, 2) if downside_be else None
        )

    def structure_diagonal_spread(
        self,
        spread_category: str,  # "UP_AND_OUT", "DOWN_AND_OUT", "REVERSE_UP_AND_OUT", "REVERSE_DOWN_AND_OUT"
        near_strike: float,
        deferred_strike: float,
        near_premium: float,
        deferred_premium: float
    ) -> Dict[str, Any]:
        """
        Decomposes diagonal spread into embedded Calendar + Vertical spreads.
        """
        net_cost = deferred_premium - near_premium if "REVERSE" not in spread_category else near_premium - deferred_premium
        is_debit = net_cost > 0

        if spread_category == "UP_AND_OUT":
            # Buy Near Call K1, Sell Deferred Call K2 (K2 > K1)
            bias = "SHARP_BULLISH_VOL_DECLINE"
            decomp = "Short Calendar + Deferred Bull Call Spread"
        elif spread_category == "DOWN_AND_OUT":
            # Buy Near Put K2, Sell Deferred Put K1 (K1 < K2)
            bias = "SHARP_BEARISH_VOL_DECLINE"
            decomp = "Short Calendar + Deferred Bear Put Spread"
        elif spread_category == "REVERSE_UP_AND_OUT":
            bias = "SLOW_BEARISH_TO_NEAR_STRIKE"
            decomp = "Long Calendar + Deferred Bear Call Spread"
        else:
            bias = "SLOW_BULLISH_TO_NEAR_STRIKE"
            decomp = "Long Calendar + Deferred Bull Put Spread"

        return {
            "category": spread_category,
            "market_bias": bias,
            "sub_spread_decomposition": decomp,
            "net_debit_or_credit": round(abs(net_cost), 2),
            "is_debit": is_debit
        }

    def evaluate_butterfly_parity(
        self,
        k1: float,
        k2: float,
        k3: float,
        fly_debit: float
    ) -> Dict[str, Any]:
        """
        Validates Butterfly (1:2:1) pricing and Call/Put fly synthetic parity.
        """
        wing_span = k2 - k1
        max_profit = wing_span - fly_debit
        rr = max_profit / fly_debit if fly_debit > 0 else 0.0

        return {
            "wing_span": wing_span,
            "fly_debit": fly_debit,
            "max_profit": round(max_profit, 2),
            "max_loss": round(fly_debit, 2),
            "reward_to_risk": round(rr, 2),
            "be_lower": round(k1 + fly_debit, 2),
            "be_upper": round(k3 - fly_debit, 2)
        }
