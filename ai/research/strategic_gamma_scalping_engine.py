"""
Strategic Gamma Scalping & Position Adjustment Engine (Module AF1 - Python)
Synthesizes the market making and strategic gamma management principles of Tony Saliba (Managing Expectations):
- "Staying Spread is Staying Alive" Market Maker Protocol
- Gamma Decay Breakeven Formula ("Paying the Rent"): Delta_S = sqrt(2 * Theta / Gamma)
- Daily Standard Deviation Band Scaling: sigma_daily = sigma_annual / sqrt(252)
- 4-Step Position Adjustment Decision Tree
- Rolling Mechanics via Vertical Spreads and Overlapping Butterflies
- Strategic Gamma Positioning Archetypes (The Big Move, S/R Repellents, Corkscrewing Triangles, Mean Reversion)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import math


@dataclass
class GammaScalpSignal:
    rebalance_shares: int        # positive = buy shares, negative = sell shares
    trigger_reason: str
    gamma_decay_breakeven: float
    current_net_delta: float
    target_net_delta: float


@dataclass
class RollOperation:
    roll_type: str               # "ROLL_LONG_CALL", "ROLL_VERTICAL_UP", etc.
    instrument_to_execute: str   # "SELL_VERTICAL_CALL_SPREAD", "SELL_CALL_BUTTERFLY", etc.
    capital_freed_credit: float
    staying_power_boost: bool


class StrategicGammaScalpingEngine:
    """
    Module AF1: Strategic Gamma Scalping & Position Adjustment Engine.
    Executes dynamic delta neutralization, calculates gamma decay rent breakevens, and generates spread roll paths.
    """

    def __init__(self, position_gamma: float = 0.15, daily_theta: float = 0.03):
        self.position_gamma = position_gamma
        self.daily_theta = abs(daily_theta)
        self.accumulated_scalp_pnl = 0.0

    def calculate_gamma_decay_breakeven(self, daily_theta: float, position_gamma: float) -> float:
        """
        Gamma Decay Formula (for equities):
        Delta_S_breakeven = sqrt( (2 * Theta) / Gamma )
        Calculates how far the stock must travel in a single day to 'pay the rent' (offset theta decay).
        """
        g = max(1e-6, position_gamma)
        th = abs(daily_theta)
        decay_move = math.sqrt((2.0 * th) / g)
        return round(decay_move, 4)

    def calculate_daily_sigma_move(self, spot_price: float, annual_volatility: float) -> Dict[str, float]:
        """
        Converts annualized volatility into daily 1-sigma, 2-sigma, and 3-sigma expected moves:
        sigma_daily = annual_volatility / sqrt(252)
        """
        daily_vol = annual_volatility / math.sqrt(252.0)
        sigma1_dollar = spot_price * daily_vol
        sigma2_dollar = sigma1_dollar * 2.0
        sigma3_dollar = sigma1_dollar * 3.0

        return {
            "daily_volatility_pct": round(daily_vol * 100.0, 4),
            "one_sigma_move": round(sigma1_dollar, 2),
            "two_sigma_move": round(sigma2_dollar, 2),
            "three_sigma_move": round(sigma3_dollar, 2),
            "upper_1sigma": round(spot_price + sigma1_dollar, 2),
            "lower_1sigma": round(spot_price - sigma1_dollar, 2)
        }

    def evaluate_gamma_scalp_step(
        self,
        current_spot: float,
        last_hedge_spot: float,
        net_delta: float,
        position_gamma: float,
        daily_theta: float,
        hedge_interval_points: float = 2.0
    ) -> Optional[GammaScalpSignal]:
        """
        Rebalances delta according to Tony Saliba's strategic straddle management routine.
        """
        move = current_spot - last_hedge_spot
        breakeven_move = self.calculate_gamma_decay_breakeven(daily_theta, position_gamma)

        if abs(move) >= hedge_interval_points:
            # If stock moved down, we are short deltas (positive gamma position). Buy shares to neutralize.
            # If stock moved up, we are long deltas. Sell shares to neutralize.
            shares_needed = -int(net_delta * 100.0) if abs(net_delta) >= 0.05 else int(-move * position_gamma * 100.0)
            
            return GammaScalpSignal(
                rebalance_shares=shares_needed,
                trigger_reason=f"Spot moved {move:+.2f} pts exceeding hedge interval ({hedge_interval_points} pts)",
                gamma_decay_breakeven=breakeven_move,
                current_net_delta=round(net_delta, 2),
                target_net_delta=0.0
            )
        return None

    def generate_roll_operation(
        self,
        current_structure: str,  # "LONG_CALL", "SHORT_CALL", "LONG_CALL_VERTICAL", "LONG_PUT_VERTICAL"
        is_rolling_up: bool,
        estimated_credit: float
    ) -> RollOperation:
        """
        Generates Saliba roll paths:
        - Roll Long Call -> Sell Vertical Call Spread
        - Roll Short Call -> Buy Vertical Call Spread
        - Roll Long Call Vertical -> Sell Call Butterfly Spread
        - Roll Long Put Vertical -> Sell Put Butterfly Spread
        """
        if current_structure == "LONG_CALL":
            action = "SELL_VERTICAL_CALL_SPREAD"
        elif current_structure == "SHORT_CALL":
            action = "BUY_VERTICAL_CALL_SPREAD"
        elif current_structure == "LONG_CALL_VERTICAL":
            action = "SELL_CALL_BUTTERFLY"
        elif current_structure == "LONG_PUT_VERTICAL":
            action = "SELL_PUT_BUTTERFLY"
        else:
            action = "LIQUIDATE_POSITION"

        return RollOperation(
            roll_type=f"{'ROLL_UP' if is_rolling_up else 'ROLL_DOWN'}_{current_structure}",
            instrument_to_execute=action,
            capital_freed_credit=round(estimated_credit, 2),
            staying_power_boost=True
        )
