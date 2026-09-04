"""
ai/self_improvement/online_trainer.py
======================================
OptionAlpha Agent — Continuous Online Learning & Model Updater

Incrementally updates the Signal Ensemble with real trade outcomes from episodic memory.
Ensures models continuously adapt to changing volatility regimes without requiring
complete offline re-training from scratch.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from loguru import logger

from agent.brain.memory import TradeMemory, TradeRecord
from ai.ensemble.signal_ensemble import SignalEnsemble
from ai.self_improvement.model_comparator import ModelComparator


class OnlineTrainer:
    """
    Manages ongoing incremental training from completed trade records.
    """

    def __init__(self, memory: Optional[TradeMemory] = None, model_dir: Optional[Path] = None):
        self.memory = memory or TradeMemory()
        self.model_dir = model_dir or Path("data/models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.model_dir / "signal_ensemble.pkl"

    def run_incremental_update(self, min_new_samples: int = 10) -> Dict:
        """
        Gathers recent completed trades, trains a candidate ensemble,
        and uses ModelComparator to safely promote if statistical criteria are met.
        """
        trades = self.memory.recent(n=100)
        if len(trades) < min_new_samples:
            logger.info("OnlineTrainer: Insufficient new trades ({}/{} needed)", len(trades), min_new_samples)
            return {"status": "skipped", "reason": "insufficient_samples"}

        # Build feature/target dataset from trades
        X_list = []
        y_list = []

        for t in trades:
            # Construct 23-dim feature vector representation
            feat = np.zeros(23, dtype=np.float32)
            feat[7] = t.iv_rank_at_open  # IV Rank
            feat[13] = t.ensemble_signal # Entry signal
            feat[14] = t.ensemble_conf   # Entry confidence
            X_list.append(feat)
            y_list.append(1 if t.was_profitable else 0)

        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.int32)

        # Split 80/20 train/validation
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        if len(X_val) == 0:
            return {"status": "skipped", "reason": "validation_set_empty"}

        # Train candidate ensemble
        candidate = SignalEnsemble()
        try:
            candidate.fit(X_train, np.where(y_train == 1, 0.05, -0.05))
        except Exception as e:
            logger.warning("OnlineTrainer fit failed: {}", e)
            return {"status": "failed", "error": str(e)}

        # Load active production model
        if self.model_path.exists():
            try:
                prod_model = SignalEnsemble.load(self.model_path)
                prod_preds = (prod_model.predict_proba(X_val) >= 0.5).astype(int)
            except Exception:
                prod_preds = np.zeros(len(y_val), dtype=int)
        else:
            prod_preds = np.zeros(len(y_val), dtype=int)

        cand_preds = (candidate.predict_proba(X_val) >= 0.5).astype(int)

        # Statistical A/B comparison
        comp = ModelComparator.compare_classifiers(y_val, prod_preds, cand_preds)

        if comp.get("promoted", False) or not self.model_path.exists():
            candidate.save(self.model_path)
            logger.success("OnlineTrainer: Deployed improved SignalEnsemble to {}", self.model_path)
            return {"status": "promoted", "comparison": comp}

        return {"status": "retained_production", "comparison": comp}
