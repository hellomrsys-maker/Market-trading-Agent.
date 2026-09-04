"""
Tactical Swing Trading & Technical Microstructure Engine (Module AA1 - Python)
Synthesizes the swing trading and price action methodologies of Warren Ray Benjamin (How to Trade Options: Swing Trading):
- ABCD Swing Pattern Recognition (Leg AB, Retracement BC, Breakout Extension CD)
- Bull & Bear Flag Momentum Formations with 2:1 Reward-to-Risk Target Rules
- Multi-Period Moving Average Ribbon (10, 20/21 EMA, 50 SMA, 100 SMA, 200/250 SMA)
- Volume-Confirmed Golden Cross and Death Cross Detectors
- Bollinger Bands (20, 2.0) Volatility Envelopes & Wick Touch Reversal Triggers
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float

    @property
    def is_bullish(self) -> bool:
        return self.close >= self.open

    @property
    def body_size(self) -> float:
        return abs(self.close - self.open)

    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low

    @property
    def is_doji(self) -> bool:
        total_range = self.high - self.low
        return total_range > 0 and (self.body_size / total_range) <= 0.10

    @property
    def is_shooting_star(self) -> bool:
        total_range = self.high - self.low
        return total_range > 0 and (self.upper_wick >= 2.0 * self.body_size) and (self.lower_wick <= 0.20 * total_range)

    @property
    def is_inverted_hammer(self) -> bool:
        total_range = self.high - self.low
        return total_range > 0 and (self.upper_wick >= 2.0 * self.body_size) and (self.lower_wick <= 0.15 * total_range)


@dataclass
class SwingSetupSignal:
    pattern_name: str
    direction: str          # "BULLISH" or "BEARISH"
    entry_price: float
    stop_loss: float
    take_profit: float
    reward_to_risk: float
    confidence_score: float


class TacticalSwingTradingEngine:
    """
    Module AA1: Tactical Swing Trading & Technical Microstructure Engine.
    Executes multi-timeframe swing trading technical analysis, flag momentum filters, and cross confirmation.
    """

    def __init__(self):
        pass

    def evaluate_abcd_pattern(
        self,
        point_a: float,
        point_b: float,
        point_c: float,
        is_bullish_trend: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates ABCD pattern targets:
        Leg AB impulse, Retracement BC (38.2% - 61.8%), and Target D projection (AB = CD or 1.272/1.618 expansion).
        """
        ab_leg = abs(point_a - point_b)
        
        if is_bullish_trend:
            # Bullish ABCD: A (low) -> B (high) -> C (pullback low) -> D (breakout high)
            retracement_ratio = (point_b - point_c) / ab_leg if ab_leg > 0 else 0.0
            point_d_target = point_c + ab_leg  # 1:1 Leg extension
            stop_loss = point_c * 0.98         # Stop under point C
            valid_retracement = 0.382 <= retracement_ratio <= 0.786
            reward_to_risk = (point_d_target - point_c) / (point_c - stop_loss) if (point_c - stop_loss) > 0 else 0.0
            
            return {
                "pattern": "BULLISH_ABCD",
                "valid_setup": valid_retracement and point_c > point_a,
                "entry_trigger": point_b,      # Breakout above B
                "point_d_target": round(point_d_target, 2),
                "stop_loss": round(stop_loss, 2),
                "reward_to_risk": round(reward_to_risk, 2)
            }
        else:
            # Bearish ABCD: A (high) -> B (low) -> C (pullback high) -> D (breakout low)
            retracement_ratio = (point_c - point_b) / ab_leg if ab_leg > 0 else 0.0
            point_d_target = point_c - ab_leg
            stop_loss = point_c * 1.02
            valid_retracement = 0.382 <= retracement_ratio <= 0.786
            reward_to_risk = (point_c - point_d_target) / (stop_loss - point_c) if (stop_loss - point_c) > 0 else 0.0

            return {
                "pattern": "BEARISH_ABCD",
                "valid_setup": valid_retracement and point_c < point_a,
                "entry_trigger": point_b,
                "point_d_target": round(point_d_target, 2),
                "stop_loss": round(stop_loss, 2),
                "reward_to_risk": round(reward_to_risk, 2)
            }

    def detect_flag_formation(
        self,
        pole_start: float,
        pole_end: float,
        pullback_extreme: float,
        current_price: float,
        volume_trend_declining: bool,
        is_bull_flag: bool = True
    ) -> Optional[SwingSetupSignal]:
        """
        Detects Bull or Bear Flag patterns with standard 2:1 Reward-to-Risk target.
        """
        pole_height = abs(pole_end - pole_start)
        if pole_height <= 0:
            return None

        if is_bull_flag:
            # Bull Flag: sharp rise (pole_start -> pole_end), slight downward pullback to pullback_extreme
            pullback_depth = (pole_end - pullback_extreme) / pole_height
            if 0.10 <= pullback_depth <= 0.50 and current_price >= pole_end:
                stop = pullback_extreme * 0.99
                risk = current_price - stop
                target = current_price + (2.0 * risk)  # 2:1 R:R
                return SwingSetupSignal(
                    pattern_name="BULL_FLAG_BREAKOUT",
                    direction="BULLISH",
                    entry_price=current_price,
                    stop_loss=round(stop, 2),
                    take_profit=round(target, 2),
                    reward_to_risk=2.0,
                    confidence_score=0.88 if volume_trend_declining else 0.72
                )
        else:
            # Bear Flag: sharp drop, slight upward consolidation
            pullback_depth = (pullback_extreme - pole_end) / pole_height
            if 0.10 <= pullback_depth <= 0.50 and current_price <= pole_end:
                stop = pullback_extreme * 1.01
                risk = stop - current_price
                target = current_price - (2.0 * risk)
                return SwingSetupSignal(
                    pattern_name="BEAR_FLAG_BREAKDOWN",
                    direction="BEARISH",
                    entry_price=current_price,
                    stop_loss=round(stop, 2),
                    take_profit=round(target, 2),
                    reward_to_risk=2.0,
                    confidence_score=0.88 if volume_trend_declining else 0.72
                )
        return None

    def evaluate_moving_average_ribbon(
        self,
        prices: List[float],
        volumes: List[float]
    ) -> Dict[str, Any]:
        """
        Computes 10 EMA, 21 EMA, 50 SMA, 100 SMA, 200 SMA and identifies Golden/Death Crosses.
        """
        if len(prices) < 200:
            return {"status": "INSUFFICIENT_DATA"}

        arr = np.array(prices)
        sma50 = np.mean(arr[-50:])
        sma100 = np.mean(arr[-100:])
        sma200 = np.mean(arr[-200:])

        # Calculate EMAs
        def calculate_ema(data, span):
            alpha = 2.0 / (span + 1.0)
            ema = [data[0]]
            for p in data[1:]:
                ema.append(alpha * p + (1.0 - alpha) * ema[-1])
            return ema[-1]

        ema10 = calculate_ema(arr, 10)
        ema21 = calculate_ema(arr, 21)

        prev_sma50 = np.mean(arr[-51:-1])
        prev_sma200 = np.mean(arr[-201:-1])

        # Golden Cross: 50 crosses above 200 SMA
        is_golden_cross = prev_sma50 <= prev_sma200 and sma50 > sma200
        # Death Cross: 50 crosses below 200 SMA
        is_death_cross = prev_sma50 >= prev_sma200 and sma50 < sma200

        # Volume confirmation
        avg_vol_20 = np.mean(volumes[-20:]) if len(volumes) >= 20 else volumes[-1]
        current_vol = volumes[-1]
        volume_confirmed = current_vol >= 1.25 * avg_vol_20

        return {
            "ema10": round(float(ema10), 2),
            "ema21": round(float(ema21), 2),
            "sma50": round(float(sma50), 2),
            "sma100": round(float(sma100), 2),
            "sma200": round(float(sma200), 2),
            "trend_state": "STRONG_BULLISH" if (ema10 > ema21 > sma50 > sma200) else "NEUTRAL_OR_BEARISH",
            "is_golden_cross": is_golden_cross and volume_confirmed,
            "is_death_cross": is_death_cross and volume_confirmed
        }
