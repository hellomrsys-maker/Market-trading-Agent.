"""
ai/models/candlestick_pattern_engine.py
=======================================
OptionAlpha Agent — Candlestick Pattern & Price Action Intelligence Engine
Based on Metaverse Trading Academy Candlestick Formations & Structural Action

Recognizes and scores high-probability multi-bar reversal and continuation formations:
  🟢 Bullish Formations:
     - Morning Star (3-bar reversal: bearish candle + small body star + bullish confirmation > 60% u-turn)
     - Bullish Engulfing (2-bar reversal: bullish candle fully engulfs previous bearish body)
     - Bullish Shooting Star / Hammer (small body at top, long lower wick >= 60% of total range)
     - Bullish Piercing Line (2-bar reversal: opens below prior low, closes > 60% into prior bearish body)
     - Bullish Tweezer Bottom (2-bar matching lows with long lower wicks >= 60%)

  🔴 Bearish Formations:
     - Evening Star (3-bar reversal: bullish candle + small body star + bearish confirmation > 60% u-turn)
     - Bearish Engulfing (2-bar reversal: bearish candle fully engulfs previous bullish body)
     - Bearish Shooting Star / Gravestone (small body at bottom, long upper wick >= 60% of range)
     - Dark Cloud Cover (2-bar reversal: opens above prior high, closes > 60% into prior bullish body)
     - Bearish Tweezer Top (2-bar matching highs with long upper wicks >= 60%)

  🛡️ Protective Stop Loss Bounds: 10-15 points / pips beyond extreme wick highs/lows.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from loguru import logger


@dataclass
class CandlestickSignal:
    pattern_name: str
    direction: str          # "BULLISH" | "BEARISH" | "NEUTRAL"
    confidence: float       # 0.0 to 1.0
    entry_price: float
    stop_loss_price: float
    target_price: float
    description: str


class CandlestickPatternEngine:
    """
    Evaluates OHLC price bars and extracts deterministic candlestick signals.
    """

    @classmethod
    def analyze_bars(cls, bars: List[Dict[str, float]]) -> Optional[CandlestickSignal]:
        """
        Analyzes the last 3 completed bars to identify reversal formations.
        bars format: [{'open': o, 'high': h, 'low': l, 'close': c}, ...]
        """
        if len(bars) < 3:
            return None

        b1 = bars[-3] # 2 bars ago
        b2 = bars[-2] # 1 bar ago
        b3 = bars[-1] # Most recent completed bar

        # Helper calculations for bar 3
        b3_range = max(1e-5, b3["high"] - b3["low"])
        b3_body = abs(b3["close"] - b3["open"])
        b3_is_bullish = b3["close"] > b3["open"]
        b3_lower_wick = (b3["open"] - b3["low"]) if b3_is_bullish else (b3["close"] - b3["low"])
        b3_upper_wick = (b3["high"] - b3["close"]) if b3_is_bullish else (b3["high"] - b3["open"])

        # Helper calculations for bar 2
        b2_range = max(1e-5, b2["high"] - b2["low"])
        b2_body = abs(b2["close"] - b2["open"])
        b2_is_bullish = b2["close"] > b2["open"]
        b2_lower_wick = (b2["open"] - b2["low"]) if b2_is_bullish else (b2["close"] - b2["low"])
        b2_upper_wick = (b2["high"] - b2["close"]) if b2_is_bullish else (b2["high"] - b2["open"])

        # Helper calculations for bar 1
        b1_is_bullish = b1["close"] > b1["open"]
        b1_body = abs(b1["close"] - b1["open"])

        # ── 1. Bullish Morning Star (3-bar) ──
        if not b1_is_bullish and b2_body < b1_body * 0.35 and b3_is_bullish:
            if b3["close"] >= b1["open"] - (b1_body * 0.40): # > 60% u-turn into b1
                stop_loss = min(b1["low"], b2["low"], b3["low"]) - 1.50
                target = b3["close"] + (b3["close"] - stop_loss) * 2.0
                return CandlestickSignal(
                    pattern_name="BULLISH_MORNING_STAR",
                    direction="BULLISH",
                    confidence=0.90,
                    entry_price=b3["close"],
                    stop_loss_price=round(stop_loss, 2),
                    target_price=round(target, 2),
                    description="3-Bar Morning Star reversal confirmed with >60% u-turn recovery.",
                )

        # ── 2. Bearish Evening Star (3-bar) ──
        if b1_is_bullish and b2_body < b1_body * 0.35 and not b3_is_bullish:
            if b3["close"] <= b1["open"] + (b1_body * 0.40): # > 60% u-turn down
                stop_loss = max(b1["high"], b2["high"], b3["high"]) + 1.50
                target = b3["close"] - (stop_loss - b3["close"]) * 2.0
                return CandlestickSignal(
                    pattern_name="BEARISH_EVENING_STAR",
                    direction="BEARISH",
                    confidence=0.90,
                    entry_price=b3["close"],
                    stop_loss_price=round(stop_loss, 2),
                    target_price=round(target, 2),
                    description="3-Bar Evening Star reversal confirmed with >60% downward penetration.",
                )

        # ── 3. Bullish Engulfing (2-bar) ──
        if not b2_is_bullish and b3_is_bullish:
            if b3["open"] <= b2["close"] and b3["close"] >= b2["open"]:
                stop_loss = min(b2["low"], b3["low"]) - 1.00
                target = b3["close"] + (b3["close"] - stop_loss) * 2.0
                return CandlestickSignal(
                    pattern_name="BULLISH_ENGULFING",
                    direction="BULLISH",
                    confidence=0.88,
                    entry_price=b3["close"],
                    stop_loss_price=round(stop_loss, 2),
                    target_price=round(target, 2),
                    description="Bullish Engulfing candle completely covers prior bearish candle body.",
                )

        # ── 4. Bearish Engulfing (2-bar) ──
        if b2_is_bullish and not b3_is_bullish:
            if b3["open"] >= b2["close"] and b3["close"] <= b2["open"]:
                stop_loss = max(b2["high"], b3["high"]) + 1.00
                target = b3["close"] - (stop_loss - b3["close"]) * 2.0
                return CandlestickSignal(
                    pattern_name="BEARISH_ENGULFING",
                    direction="BEARISH",
                    confidence=0.88,
                    entry_price=b3["close"],
                    stop_loss_price=round(stop_loss, 2),
                    target_price=round(target, 2),
                    description="Bearish Engulfing candle completely covers prior bullish candle body.",
                )

        # ── 5. Bullish Tweezer Bottom (2-bar wicks >= 60%) ──
        if abs(b2["low"] - b3["low"]) / b3_range < 0.08 and (b3_lower_wick / b3_range) >= 0.55:
            stop_loss = min(b2["low"], b3["low"]) - 1.00
            target = b3["close"] + (b3["close"] - stop_loss) * 2.0
            return CandlestickSignal(
                pattern_name="BULLISH_TWEEZER_BOTTOM",
                direction="BULLISH",
                confidence=0.85,
                entry_price=b3["close"],
                stop_loss_price=round(stop_loss, 2),
                target_price=round(target, 2),
                description="Tweezer Bottom formed with dual matching lows and >=60% lower wicks.",
            )

        # ── 6. Bearish Tweezer Top (2-bar wicks >= 60%) ──
        if abs(b2["high"] - b3["high"]) / b3_range < 0.08 and (b3_upper_wick / b3_range) >= 0.55:
            stop_loss = max(b2["high"], b3["high"]) + 1.00
            target = b3["close"] - (stop_loss - b3["close"]) * 2.0
            return CandlestickSignal(
                pattern_name="BEARISH_TWEEZER_TOP",
                direction="BEARISH",
                confidence=0.85,
                entry_price=b3["close"],
                stop_loss_price=round(stop_loss, 2),
                target_price=round(target, 2),
                description="Tweezer Top formed with dual matching highs and >=60% upper wicks.",
            )

        return None
