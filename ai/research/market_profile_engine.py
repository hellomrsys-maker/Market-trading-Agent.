"""
ai/research/market_profile_engine.py
====================================
OptionAlpha Agent — Dalton Auction Market Profile & Multi-Timeframe Engine
Based on "Markets in Profile: Profiting from the Auction Process" by James F. Dalton, Robert B. Dalton, Eric T. Jones (Wiley)

Key Capabilities:
  1. TPO (Time-Price Opportunity) & Volume Value Area:
     - Point of Control (POC / PPOC): Longest horizontal TPO line (highest accepted fair value).
     - Value Area High (VAH) & Value Area Low (VAL): 70% of total TPO distribution (1 standard deviation).
  2. 4 Auction Opening Classifications:
     - OPEN_DRIVE: Highest directional confidence; market explodes out of the gate with no opening retest.
     - OPEN_TEST_DRIVE: Market tests beyond key reference level, rejects, then drives in opposite direction.
     - OPEN_REJECTION_REVERSE: Explores in one direction, forms single-print tail, auctions back through open.
     - OPEN_AUCTION: Trades above and below open within previous range; low initial confidence (patient wait).
  3. Profile Morphology & Structural Signatures:
     - ELONGATED_TREND: High conviction, value migration across multiple timeframes.
     - P_SHAPE: Short covering rally with upper loop (lacks new aggressive buyers; early warning of exhaustion).
     - B_SHAPE: Long liquidation break with lower loop (patient longer-term buyers accumulating).
     - BALANCED_BELL: Symmetrical distribution (favor mean-reversion and fading bracket extremes).
  4. One-Timeframing Auction Detection:
     - Tracks continuous unidirectional bar sequences (prohibits countertrend fading).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from loguru import logger


@dataclass
class MarketProfileStructure:
    symbol: str
    poc_price: float
    vah_price: float
    val_price: float
    initial_balance_high: float
    initial_balance_low: float
    open_type: str                  # "OPEN_DRIVE" | "OPEN_TEST_DRIVE" | "OPEN_REJECTION_REVERSE" | "OPEN_AUCTION"
    profile_morphology: str         # "ELONGATED_TREND" | "P_SHAPE_SHORT_COVERING" | "B_SHAPE_LONG_LIQUIDATION" | "BALANCED_BELL"
    is_one_timeframing: bool
    one_timeframing_direction: str  # "UP" | "DOWN" | "NONE"
    is_balanced_bracket: bool
    asymmetric_trade_recommendation: str


class DaltonMarketProfileEngine:
    """
    Constructs and interprets Market Profile distributions and auction dynamics.
    """

    @classmethod
    def calculate_tpo_profile(
        cls,
        symbol: str,
        tpo_bars_30m: List[Dict[str, float]], # [{'open': o, 'high': h, 'low': l, 'close': c, 'period': 'B'}, ...]
    ) -> MarketProfileStructure:
        """
        Builds the 30-minute TPO matrix and identifies POC, VAH, VAL, and Opening classification.
        """
        if not tpo_bars_30m:
            return MarketProfileStructure(
                symbol=symbol, poc_price=100.0, vah_price=101.0, val_price=99.0,
                initial_balance_high=100.5, initial_balance_low=99.5,
                open_type="OPEN_AUCTION", profile_morphology="BALANCED_BELL",
                is_one_timeframing=False, one_timeframing_direction="NONE",
                is_balanced_bracket=True, asymmetric_trade_recommendation="WAIT_FOR_BALANCE_BREAK",
            )

        # 1. Initial Balance (First 2 periods: B and C)
        ib_bars = tpo_bars_30m[:2]
        ib_high = max(b["high"] for b in ib_bars)
        ib_low = min(b["low"] for b in ib_bars)

        # 2. Extract price array and determine POC
        all_highs = [b["high"] for b in tpo_bars_30m]
        all_lows = [b["low"] for b in tpo_bars_30m]
        all_closes = [b["close"] for b in tpo_bars_30m]
        day_high = max(all_highs)
        day_low = min(all_lows)
        day_open = tpo_bars_30m[0]["open"]
        day_close = tpo_bars_30m[-1]["close"]

        # Histogram representation (TPO counts)
        prices = np.linspace(day_low, day_high, 20)
        tpo_counts = np.zeros(len(prices))
        for b in tpo_bars_30m:
            mask = (prices >= b["low"]) & (prices <= b["high"])
            tpo_counts[mask] += 1

        poc_idx = int(np.argmax(tpo_counts))
        poc_price = float(prices[poc_idx])

        # Value Area (70% of TPOs around POC)
        total_tpos = np.sum(tpo_counts)
        target_tpos = total_tpos * 0.70
        curr_tpos = tpo_counts[poc_idx]
        up_idx, down_idx = poc_idx, poc_idx

        while curr_tpos < target_tpos and (up_idx < len(prices) - 1 or down_idx > 0):
            up_sum = tpo_counts[up_idx + 1] if up_idx < len(prices) - 1 else 0
            down_sum = tpo_counts[down_idx - 1] if down_idx > 0 else 0
            if up_sum >= down_sum and up_idx < len(prices) - 1:
                up_idx += 1
                curr_tpos += tpo_counts[up_idx]
            elif down_idx > 0:
                down_idx -= 1
                curr_tpos += tpo_counts[down_idx]
            else:
                break

        vah_price = float(prices[up_idx])
        val_price = float(prices[down_idx])

        # 3. Determine Open Type (Dalton Chapter 8)
        b1 = tpo_bars_30m[0]
        if abs(b1["close"] - b1["open"]) / max(1e-4, b1["high"] - b1["low"]) > 0.75:
            open_type = "OPEN_DRIVE"
        elif len(tpo_bars_30m) >= 2 and (tpo_bars_30m[1]["high"] > ib_high or tpo_bars_30m[1]["low"] < ib_low):
            open_type = "OPEN_TEST_DRIVE"
        elif (day_close > day_open and day_low < day_open - (day_high - day_low) * 0.20) or \
             (day_close < day_open and day_high > day_open + (day_high - day_low) * 0.20):
            open_type = "OPEN_REJECTION_REVERSE"
        else:
            open_type = "OPEN_AUCTION"

        # 4. Profile Morphology (Dalton Chapters 4 & 7)
        # Check skew of TPO distribution: upper-heavy = 'p', lower-heavy = 'b', elongated = trend
        mean_price = (day_high + day_low) / 2.0
        if (day_high - day_low) > (ib_high - ib_low) * 2.2:
            morphology = "ELONGATED_TREND"
        elif poc_price > mean_price + (day_high - day_low) * 0.15:
            morphology = "P_SHAPE_SHORT_COVERING"
        elif poc_price < mean_price - (day_high - day_low) * 0.15:
            morphology = "B_SHAPE_LONG_LIQUIDATION"
        else:
            morphology = "BALANCED_BELL"

        # 5. One-Timeframing Check (consecutive higher lows or lower highs)
        is_otf_up = all(tpo_bars_30m[i]["low"] >= tpo_bars_30m[i - 1]["low"] - 0.05 for i in range(1, len(tpo_bars_30m)))
        is_otf_down = all(tpo_bars_30m[i]["high"] <= tpo_bars_30m[i - 1]["high"] + 0.05 for i in range(1, len(tpo_bars_30m)))
        if is_otf_up:
            otf = True
            otf_dir = "UP"
        elif is_otf_down:
            otf = True
            otf_dir = "DOWN"
        else:
            otf = False
            otf_dir = "NONE"

        # Asymmetric recommendation
        if morphology == "ELONGATED_TREND":
            rec = "GO_WITH_TREND_DO_NOT_FADE"
        elif morphology == "P_SHAPE_SHORT_COVERING":
            rec = "LOOK_FOR_SHORT_FADE_AT_UPPER_EXTREME"
        elif morphology == "B_SHAPE_LONG_LIQUIDATION":
            rec = "LOOK_FOR_LONG_REVERSAL_AT_LOWER_EXTREME"
        else:
            rec = "FADE_BRACKET_EXTREMES_REVERSION_TO_MEAN"

        return MarketProfileStructure(
            symbol=symbol,
            poc_price=round(poc_price, 2),
            vah_price=round(vah_price, 2),
            val_price=round(val_price, 2),
            initial_balance_high=round(ib_high, 2),
            initial_balance_low=round(ib_low, 2),
            open_type=open_type,
            profile_morphology=morphology,
            is_one_timeframing=otf,
            one_timeframing_direction=otf_dir,
            is_balanced_bracket=morphology == "BALANCED_BELL",
            asymmetric_trade_recommendation=rec,
        )
