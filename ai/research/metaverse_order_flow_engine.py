"""
ai/research/metaverse_order_flow_engine.py
==========================================
OptionAlpha Agent — Metaverse Open Interest & Order Flow Data Discovery

Implements Open Interest trends and Order Flow combinations defined in 
"Data Discovery: Open Interest + Order Flow" by Metaverse Trading Academy.

========================================================================================
MASTER MANDATE & POLYGLOT COMPUTING RULE APPLIED
========================================================================================
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
import numpy as np
from loguru import logger

class OrderFlowEngine:
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32) # Zero-Bridge Proxy

    def analyze_oi_and_volume(self, price_trend: str, oi_trend: str, volume_trend: str) -> Dict:
        """
        Matrix decoding of Price, Volume, and Open Interest trends to infer market sentiment.
        """
        inference = "NEUTRAL"
        confidence = 0.5
        
        # 1. Long Build Up
        if price_trend == "RISING" and oi_trend == "RISING" and volume_trend == "RISING":
            inference = "STRONG_UPTREND_LONG_BUILDUP"
            confidence = 0.95
        # 2. Short Covering
        elif price_trend == "RISING" and oi_trend == "FALLING" and volume_trend == "FALLING":
            inference = "WEAK_UPTREND_SHORT_COVERING"
            confidence = 0.60
        # 3. Short Build Up
        elif price_trend == "FALLING" and oi_trend == "RISING" and volume_trend == "RISING":
            inference = "STRONG_DOWNTREND_SHORT_BUILDUP"
            confidence = 0.90
        # 4. Long Unwinding
        elif price_trend == "FALLING" and oi_trend == "FALLING" and volume_trend == "FALLING":
            inference = "WEAK_DOWNTREND_LONG_UNWINDING"
            confidence = 0.60
            
        return {
            "inference": inference,
            "confidence": confidence,
            "action_bias": "FOLLOW_TREND" if confidence > 0.8 else "AWAIT_CONFIRMATION"
        }

    def detect_liquidity_support_resistance(self, current_price: float, limit_buyers_volume: int, limit_sellers_volume: int) -> str:
        """
        Order Flow Analysis focuses on the behavior of limit orders (buy and sell), giving traders
        a view of the supply and demand dynamics at different price levels.
        """
        imbalance_ratio = limit_buyers_volume / max(1, limit_sellers_volume)
        
        if imbalance_ratio > 3.0:
            return "STRONG_SUPPORT_BUY_LIMIT_WALL"
        elif imbalance_ratio < 0.33:
            return "STRONG_RESISTANCE_SELL_LIMIT_WALL"
            
        return "BALANCED_LIQUIDITY"
