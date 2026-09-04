"""
agent/fallback_signal.py
=========================
OptionAlpha Agent — Rule-Based Fallback Signal Engine

Activates automatically if deep learning inference (Transformer/PPO/Ensemble)
encounters unexpected numerical runtime exceptions or missing torch/onnx dependencies.
Ensures zero-downtime uninterrupted market participation.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from loguru import logger


class FallbackSignalEngine:
    """
    Heuristic rule-based options decision engine.
    Uses classical quantitative metrics: IV Rank, 20-day Momentum, VIX thresholds.
    """

    @staticmethod
    def evaluate_symbol(
        symbol: str,
        iv_rank: float,
        momentum_20d: float,
        vix: float = 18.0
    ) -> Tuple[bool, str, float]:
        """
        Returns (should_trade: bool, strategy_recommendation: str, confidence: float)
        """
        # Circuit Breaker: extreme volatility
        if vix > 35.0:
            return False, "CASH_HOLD", 0.0

        # High IV Rank -> Iron Condor
        if iv_rank >= 35.0:
            confidence = min(0.95, 0.50 + (iv_rank / 100.0) * 0.40)
            return True, "IRON_CONDOR", confidence

        # Moderate IV & Neutral/Positive Momentum -> Wheel CSP
        if iv_rank >= 15.0 and momentum_20d >= -0.05:
            confidence = 0.70 if momentum_20d > 0.0 else 0.55
            return True, "WHEEL_CSP", confidence

        # Low IV / negative trend -> Hold cash or small position
        return False, "CASH_HOLD", 0.30
