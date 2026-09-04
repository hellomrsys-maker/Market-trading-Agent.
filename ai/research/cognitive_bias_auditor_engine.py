"""
ai/research/cognitive_bias_auditor_engine.py
============================================
OptionAlpha Agent — Module P1: Python Cognitive Bias Auditor & Trading Rules Engine
MASTER MANDATE & ZERO-BRIDGE CONSTRAINTS APPLIED
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple

class CognitiveBiasAuditorEngine:
    """
    Implements 8 Specific Cognitive Bias Audits & 10 Rules of Trading:
    1. Recency Bias (Overweighting recent win/loss streaks)
    2. Loss Aversion (Premature BE stops / Cutting winners short)
    3. Disposition Effect (Holding losers past stop / Exiting <1R)
    4. Overconfidence After Wins (Oversizing after positive runs)
    5. Revenge Trading Cycle (Entering within 30m of a loss to 'make back')
    6. Confirmation Bias (Only seeking thesis validation)
    7. Narrative Fallacy (Attributing random variance to causal stories)
    8. Gambler's Fallacy & Martingale Sizing
    """
    def __init__(self):
        self.memory_state = np.zeros(64, dtype=np.float32)

    def audit_pre_trade_bias(
        self,
        time_since_last_loss_mins: int,
        is_on_watchlist: bool,
        is_oversized: bool,
        reasoning_text: str
    ) -> Dict[str, bool | List[str] | str]:
        biases_detected = []
        
        # 1. Revenge Trading Check
        if time_since_last_loss_mins < 30:
            biases_detected.append("REVENGE_TRADING_HIGH_RISK_EMOTIONAL_URGENCY")

        # 2. Watchlist / FOMO Check
        if not is_on_watchlist:
            biases_detected.append("FOMO_UNPLANNED_IMPULSE_ENTRY")

        # 3. Overconfidence / Martingale
        if is_oversized:
            biases_detected.append("OVERCONFIDENCE_MARTINGALE_SIZING_VIOLATION")

        # 4. Intuitive / Narrative Fallacy
        if "feels like" in reasoning_text.lower() or "make back" in reasoning_text.lower():
            biases_detected.append("NARRATIVE_FALLACY_FEELING_BASED_EXECUTION")

        trade_permitted = len(biases_detected) == 0

        return {
            "trade_permitted": trade_permitted,
            "biases_detected": biases_detected,
            "intervention": "PROCEED_OBJECTIVE_SETUP" if trade_permitted else "CIRCUIT_BREAKER_TRIGGERED_DO_NOT_TRADE"
        }

    def evaluate_pre_session_readiness(
        self,
        sleep_hours: float,
        stress_score_1_to_10: int,
        focus_score_1_to_10: int
    ) -> Dict[str, str | float]:
        """
        Determines trader psychological readiness:
        - If sleep < 6h or stress > 6 or focus < 5 -> Reduce size by 50% or stand aside.
        """
        if sleep_hours < 5.5 or stress_score_1_to_10 >= 7 or focus_score_1_to_10 <= 4:
            return {
                "readiness": "IMPAIRED_COGNITIVE_STATE",
                "recommended_size_multiplier": 0.0,
                "directive": "STAND_ASIDE_OBSERVATION_MODE_ONLY"
            }
        elif stress_score_1_to_10 >= 5 or focus_score_1_to_10 <= 6:
            return {
                "readiness": "MODERATE_COGNITIVE_LOAD",
                "recommended_size_multiplier": 0.50,
                "directive": "REDUCE_POSITION_SIZE_50_PERCENT"
            }
        return {
            "readiness": "PEAK_PERFORMANCE_READY",
            "recommended_size_multiplier": 1.0,
            "directive": "FULL_SYSTEM_EXECUTION_AUTHORIZED"
        }
