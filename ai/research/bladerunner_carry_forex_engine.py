"""
Forex Microstructure, Bladerunner 20-EMA & Carry Trade Engine (Module BG1 - Python)
Synthesizes Odin Velez's "Day Trading Forex":
- Bladerunner 20-EMA Dynamic Polarity Ribbon & Trend Reversal Re-tests
- Multi-Currency Interest Rate Carry Trade Daily Rollover Yield
- Kelly Criterion Optimal Bet Sizing (f = W - (1-W)/R) with 25% Maximum Capital Cap
"""

from typing import Dict, List, Any


class BladerunnerCarryForexEngine:
    def __init__(self, max_kelly_fraction: float = 0.25):
        self.max_kelly = max_kelly_fraction

    def evaluate_bladerunner_setup(
        self,
        current_spot: float,
        ema_20_level: float,
        is_candle_rejected: bool,
        is_breakout_confirmed: bool
    ) -> Dict[str, Any]:
        """
        Bladerunner 20-EMA Price Action:
        Spot > 20 EMA + Re-test/Bounce -> Bullish continuation.
        Spot < 20 EMA + Re-test/Reject -> Bearish continuation.
        """
        is_above_ema = current_spot > ema_20_level
        polarity = "BULLISH_ABOVE_BLADE" if is_above_ema else "BEARISH_BELOW_BLADE"

        trade_signal = "NO_SETUP_WAIT"
        if is_above_ema and is_candle_rejected and is_breakout_confirmed:
            trade_signal = "ENTER_LONG_ON_BLADE_BOUNCE"
        elif not is_above_ema and is_candle_rejected and is_breakout_confirmed:
            trade_signal = "ENTER_SHORT_ON_BLADE_REJECTION"

        return {
            "spot_price": current_spot,
            "ema_20_level": ema_20_level,
            "polarity": polarity,
            "is_candle_rejected": is_candle_rejected,
            "trade_signal": trade_signal
        }

    def calculate_daily_carry_yield(
        self,
        long_currency_rate_pct: float,
        short_currency_rate_pct: float,
        position_units: float,
        unit_price_usd: float = 1.0
    ) -> Dict[str, Any]:
        """
        Daily Carry Trade Rollover = (Rate_long - Rate_short) * Units / 365
        """
        rate_diff = (long_currency_rate_pct - short_currency_rate_pct) / 100.0
        daily_interest_dollars = (rate_diff * (position_units * unit_price_usd)) / 365.0
        is_positive_carry = daily_interest_dollars > 0.0

        return {
            "long_rate_pct": long_currency_rate_pct,
            "short_rate_pct": short_currency_rate_pct,
            "rate_differential_pct": round((long_currency_rate_pct - short_currency_rate_pct), 2),
            "daily_interest_earned": round(daily_interest_dollars, 2),
            "annualized_carry_dollars": round(daily_interest_dollars * 365.0, 2),
            "is_positive_carry": is_positive_carry
        }

    def compute_kelly_fraction(
        self,
        win_probability: float,
        win_loss_ratio: float
    ) -> Dict[str, Any]:
        """
        Kelly Criterion: f = W - ((1 - W) / R)
        """
        w = max(0.01, min(0.99, win_probability))
        r = max(0.01, win_loss_ratio)

        kelly_val = w - ((1.0 - w) / r)
        optimal_alloc = max(0.0, min(self.max_kelly, kelly_val))

        return {
            "win_probability": w,
            "win_loss_ratio": r,
            "raw_kelly_percentage": round(kelly_val * 100.0, 2),
            "recommended_allocation_pct": round(optimal_alloc * 100.0, 2),
            "is_viable_edge": kelly_val > 0.0
        }
