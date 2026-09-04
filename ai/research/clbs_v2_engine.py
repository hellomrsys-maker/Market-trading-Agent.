"""
ai/research/clbs_v2_engine.py
=============================
OptionAlpha Agent — CLBS V2 Dealer-First Market Intelligence Engine
Based on The CLBS Doctrine (Dealer Gamma, Auction Market Profile, VWAP Equilibrium)

Institutional Desks Analyzed:
  - Citadel Securities, Jane Street, Susquehanna (SIG), Optiver, IMC, Jump, DRW, Flow Traders, Virtu, Goldman Sachs.

Core Intelligence Pillars:
  1. Dealer Net Gamma Exposure (GEX):
     - Long Gamma (> 0): Dealers buy dips / sell rallies -> Volatility compression, range rotation, pinning.
     - Short Gamma (< 0): Dealers sell dips / buy rallies -> Volatility expansion, momentum acceleration, gamma flips.
     - Gamma Flip Point: Spot price where net GEX crosses 0.0.
  2. Auction Theory & Market Profile:
     - Point of Control (POC), Value Area High (VAH = +1 sigma), Value Area Low (VAL = -1 sigma).
     - Balance vs Imbalance: Acceptance inside Value Area vs Rejection & Extension.
  3. VWAP Equilibrium:
     - Intraday VWAP, Weekly VWAP, Monthly Anchored VWAP standard deviation bands (+1, +2, -1, -2 sigma).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from loguru import logger


@dataclass
class CLBSMarketIntelligence:
    symbol: str
    net_gamma_dollars: float         # Net Dealer GEX ($ Millions per 1% move)
    gamma_regime: str                # "LONG_GAMMA_PINNING" | "SHORT_GAMMA_EXPANSION"
    gamma_flip_strike: float         # Critical transition pivot
    is_long_gamma: bool
    poc_price: float                 # Market Profile Point of Control
    vah_price: float                 # Value Area High (70% volume bound)
    val_price: float                 # Value Area Low (70% volume bound)
    vwap_intraday: float
    vwap_distance_pct: float
    auction_state: str               # "VALUE_ACCEPTANCE" | "AUCTION_IMBALANCE_EXPANSION"
    recommended_positioning: str     # "MEAN_REVERSION_RANGE" | "MOMENTUM_BREAKOUT_HEDGE"


class CLBSV2IntelligenceEngine:
    """
    Calculates dealer inventory, net gamma exposure, and auction profiles.
    """

    @classmethod
    def compute_dealer_gamma_exposure(
        cls,
        spot_price: float,
        chain_contracts: List[Dict[str, Any]],
        multiplier: float = 100.0,
    ) -> Tuple[float, float, str]:
        """
        Computes Total Net GEX in $ Millions and estimates the Gamma Flip strike.
        Net GEX = Sum(Call_Gamma * Call_OI) - Sum(Put_Gamma * Put_OI) * Spot * Spot * 0.01
        """
        total_call_gex = 0.0
        total_put_gex = 0.0
        strike_gex_map: Dict[float, float] = {}

        for c in chain_contracts:
            strike = float(c.get("strike", spot_price))
            gamma = float(c.get("gamma", 0.02))
            oi = float(c.get("open_interest", 1000.0))
            is_call = bool(c.get("is_call", True))

            # Spot * 0.01 * Gamma * OI * multiplier * Spot
            dollar_gamma = gamma * oi * multiplier * (spot_price ** 2) * 0.01 / 1_000_000.0 # $M

            if is_call:
                total_call_gex += dollar_gamma
                strike_gex_map[strike] = strike_gex_map.get(strike, 0.0) + dollar_gamma
            else:
                total_put_gex += dollar_gamma
                strike_gex_map[strike] = strike_gex_map.get(strike, 0.0) - dollar_gamma

        net_gex = total_call_gex - total_put_gex
        gamma_regime = "LONG_GAMMA_PINNING" if net_gex >= 0 else "SHORT_GAMMA_EXPANSION"

        # Find strike closest to zero GEX
        if strike_gex_map:
            sorted_strikes = sorted(strike_gex_map.keys())
            gamma_flip_strike = min(sorted_strikes, key=lambda s: abs(strike_gex_map[s]))
        else:
            gamma_flip_strike = spot_price

        return round(net_gex, 2), gamma_flip_strike, gamma_regime

    @classmethod
    def compute_auction_profile_and_vwap(
        cls,
        price_bars: List[Dict[str, float]],
        spot_price: float,
    ) -> Tuple[float, float, float, float, str]:
        """
        Computes POC, VAH, VAL, and VWAP Equilibrium over price bars.
        """
        if not price_bars:
            return spot_price, spot_price * 1.01, spot_price * 0.99, spot_price, "VALUE_ACCEPTANCE"

        closes = np.array([b["close"] for b in price_bars])
        volumes = np.array([b.get("volume", 1000.0) for b in price_bars])

        # VWAP
        total_vol = max(1.0, np.sum(volumes))
        vwap = np.sum(closes * volumes) / total_vol

        # Profile POC (mode of volume-weighted distribution)
        hist, bin_edges = np.histogram(closes, bins=15, weights=volumes)
        max_bin = np.argmax(hist)
        poc = (bin_edges[max_bin] + bin_edges[max_bin + 1]) / 2.0

        # Value Area (70% mass around POC)
        std_price = np.std(closes)
        vah = poc + (std_price * 1.0)
        val = poc - (std_price * 1.0)

        # Auction state
        if val <= spot_price <= vah:
            auction_state = "VALUE_ACCEPTANCE"
        else:
            auction_state = "AUCTION_IMBALANCE_EXPANSION"

        return round(poc, 2), round(vah, 2), round(val, 2), round(vwap, 2), auction_state

    @classmethod
    def analyze_market(
        cls,
        symbol: str,
        spot_price: float,
        chain_contracts: List[Dict[str, Any]],
        price_bars: List[Dict[str, float]],
    ) -> CLBSMarketIntelligence:
        """
        Synthesizes complete CLBS V2 Dealer & Structural Intelligence.
        """
        net_gex, gamma_flip, regime = cls.compute_dealer_gamma_exposure(spot_price, chain_contracts)
        poc, vah, val, vwap, auction_state = cls.compute_auction_profile_and_vwap(price_bars, spot_price)

        vwap_dist = round(((spot_price - vwap) / vwap) * 100.0, 2)
        pos = "MEAN_REVERSION_RANGE" if regime == "LONG_GAMMA_PINNING" else "MOMENTUM_BREAKOUT_HEDGE"

        return CLBSMarketIntelligence(
            symbol=symbol,
            net_gamma_dollars=net_gex,
            gamma_regime=regime,
            gamma_flip_strike=gamma_flip,
            is_long_gamma=net_gex >= 0,
            poc_price=poc,
            vah_price=vah,
            val_price=val,
            vwap_intraday=vwap,
            vwap_distance_pct=vwap_dist,
            auction_state=auction_state,
            recommended_positioning=pos,
        )
