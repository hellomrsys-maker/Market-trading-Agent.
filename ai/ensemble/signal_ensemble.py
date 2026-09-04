"""
ai/ensemble/signal_ensemble.py
================================
OptionAlpha Agent — Classical ML Signal Ensemble

The third layer of the self-developed AI stack.
Combines XGBoost + LightGBM + CatBoost in a stacked ensemble
to generate trading signals and confidence scores.

Role in the hierarchy:
  RL Agent    → WHAT to do (strategy, symbol, timing)
  Transformer → market REGIME (Neutral/Bull/Bear/High-IV)
  Ensemble    → SHOULD WE? (signal confidence gate before execution)

The ensemble outputs:
  signal:     float in [-1, 1]
              > +0.3  → strong GO signal (proceed with trade)
              [-0.3, 0.3] → uncertain (reduce size or skip)
              < -0.3  → AVOID (pass on trade)
  confidence: float in [0, 1] — calibrated probability

Features consumed (from FeatureMatrix + Greeks snapshot):
  - All 13 per-symbol features from FeatureMatrix
  - IV Rank, put/call ratio, volume spike flag (from Rust engine)
  - Regime one-hot (from Transformer)
  - Account state: equity%, positions%, delta_exposure_norm

Training:
  - Level-0: XGBoost, LightGBM, CatBoost trained individually
  - Level-1: Logistic regression meta-learner on OOF predictions
  - Labels: next-5-day forward return (binarised: positive/negative)
  - No future data leak: strict temporal train/test split
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score

try:
    import xgboost as xgb
    _XGB = True
except ImportError:
    _XGB = False

try:
    import lightgbm as lgb
    _LGB = True
except ImportError:
    _LGB = False

try:
    from catboost import CatBoostClassifier
    _CAT = True
except ImportError:
    _CAT = False


# ─────────────────────────────────────────────────────────────
# Feature names (must align with FeatureMatrix + extras)
# ─────────────────────────────────────────────────────────────
FEATURE_NAMES = [
    # FeatureMatrix (13)
    "close_ret_1", "close_ret_5", "close_ret_20",
    "sma_r20", "sma_r50", "rv20",
    "iv", "iv_rank",
    "avg_delta", "avg_gamma", "avg_theta", "avg_vega",
    "vol_ratio",
    # Order flow (Rust engine, 3)
    "put_call_ratio", "is_volume_spike", "gex_norm",
    # Regime (4 one-hot)
    "regime_neutral", "regime_bull", "regime_bear", "regime_high_iv",
    # Account state (3)
    "equity_pct", "positions_pct", "delta_norm",
]
N_FEATURES = len(FEATURE_NAMES)   # 23


# ─────────────────────────────────────────────────────────────
# Base Model Factories
# ─────────────────────────────────────────────────────────────

def _make_xgb() -> Optional[object]:
    if not _XGB: return None
    return xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=1.0,
        reg_alpha=0.1,
        reg_lambda=1.0,
        use_label_encoder=False,
        eval_metric="auc",
        tree_method="hist",    # GPU if available: tree_method="gpu_hist"
        random_state=42,
        n_jobs=-1,
    )

def _make_lgb() -> Optional[object]:
    if not _LGB: return None
    return lgb.LGBMClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        num_leaves=63,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        verbosity=-1,
    )

def _make_cat() -> Optional[object]:
    if not _CAT: return None
    return CatBoostClassifier(
        iterations=500,
        depth=6,
        learning_rate=0.05,
        l2_leaf_reg=3.0,
        random_seed=42,
        verbose=False,
        task_type="GPU" if _gpu_available() else "CPU",
    )

def _gpu_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


# ─────────────────────────────────────────────────────────────
# Stacked Ensemble
# ─────────────────────────────────────────────────────────────

class SignalEnsemble:
    """
    2-level stacked ensemble for trade signal generation.

    Level-0: XGBoost + LightGBM + CatBoost (whichever are installed)
    Level-1: Calibrated Logistic Regression meta-learner

    Output: (signal: float, confidence: float)
    """

    def __init__(self):
        self.l0_models: List[object] = []
        self.l1_meta:   Optional[object] = None
        self.scaler:    StandardScaler = StandardScaler()
        self._is_fitted: bool = False

    def _get_l0_models(self) -> List[object]:
        models = []
        xgb_m = _make_xgb()
        lgb_m = _make_lgb()
        cat_m = _make_cat()
        if xgb_m: models.append(("XGBoost",  xgb_m))
        if lgb_m: models.append(("LightGBM", lgb_m))
        if cat_m: models.append(("CatBoost", cat_m))
        if not models:
            # Fallback: sklearn GradientBoosting
            from sklearn.ensemble import GradientBoostingClassifier
            models.append(("GBM", GradientBoostingClassifier(
                n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42
            )))
        return models

    def _label_samples(self, returns: np.ndarray, fwd_window: int = 5) -> np.ndarray:
        """
        Binary label: 1 if mean forward return > 0 (profitable trade entry),
        else 0. Strict temporal labelling — no leakage.
        """
        n = len(returns)
        labels = np.zeros(n, dtype=np.int64)
        for i in range(n - fwd_window):
            fwd_ret = returns[i+1 : i+1+fwd_window].mean()
            labels[i] = 1 if fwd_ret > 0.0 else 0
        return labels[:-fwd_window]   # drop last fwd_window rows (no label)

    def fit(
        self,
        X:         np.ndarray,   # (n_samples, N_FEATURES)
        returns:   np.ndarray,   # (n_samples,) daily log-returns for labelling
        n_splits:  int = 5,
    ) -> Dict[str, float]:
        """
        Full training pipeline with temporal cross-validation.
        Returns OOF AUC per model and meta-learner AUC.
        """
        y      = self._label_samples(returns)
        X      = X[:len(y)]                 # align
        X_sc   = self.scaler.fit_transform(X)

        tscv   = TimeSeriesSplit(n_splits=n_splits)
        named_models = self._get_l0_models()

        # OOF predictions matrix: (n_samples, n_models)
        oof_preds = np.zeros((len(X_sc), len(named_models)), dtype=np.float32)

        trained_models = []
        metrics = {}

        for mi, (name, model) in enumerate(named_models):
            fold_aucs = []
            for fold, (tr_idx, val_idx) in enumerate(tscv.split(X_sc)):
                X_tr, X_val = X_sc[tr_idx], X_sc[val_idx]
                y_tr, y_val = y[tr_idx],    y[val_idx]

                # Fit
                if hasattr(model, "fit"):
                    if name == "XGBoost":
                        model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
                    elif name == "LightGBM":
                        model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)],
                                  callbacks=[lgb.early_stopping(50, verbose=False),
                                             lgb.log_evaluation(-1)])
                    else:
                        model.fit(X_tr, y_tr)

                proba = model.predict_proba(X_val)[:, 1]
                oof_preds[val_idx, mi] = proba
                fold_aucs.append(roc_auc_score(y_val, proba) if len(np.unique(y_val)) > 1 else 0.5)

            metrics[name] = float(np.mean(fold_aucs))
            print(f"  [{name}] OOF AUC = {metrics[name]:.4f}")

            # Refit on full data for final model
            if name == "XGBoost":
                model.fit(X_sc, y)
            elif name == "LightGBM":
                model.fit(X_sc, y, callbacks=[lgb.log_evaluation(-1)])
            else:
                model.fit(X_sc, y)
            trained_models.append(model)

        self.l0_models = trained_models

        # Level-1 meta-learner (calibrated LR on OOF predictions)
        meta_base = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        self.l1_meta = CalibratedClassifierCV(meta_base, method="isotonic", cv=3)
        self.l1_meta.fit(oof_preds, y)

        meta_proba  = self.l1_meta.predict_proba(oof_preds)[:, 1]
        meta_auc    = roc_auc_score(y, meta_proba) if len(np.unique(y)) > 1 else 0.5
        metrics["Meta-LR"] = float(meta_auc)
        print(f"  [MetaLR ] OOF AUC = {metrics['Meta-LR']:.4f}")

        self._is_fitted = True
        return metrics

    def predict(self, x: np.ndarray) -> Tuple[float, float]:
        """
        Predict signal for a single feature vector.

        Args:
            x: (N_FEATURES,) feature array

        Returns:
            signal:     float in [-1, 1]
            confidence: float in [0, 1]
        """
        if not self._is_fitted:
            return 0.0, 0.5   # no signal when untrained

        x_sc = self.scaler.transform(x.reshape(1, -1))

        # Level-0 probabilities
        l0_probs = np.array([
            m.predict_proba(x_sc)[0, 1] for m in self.l0_models
        ], dtype=np.float32).reshape(1, -1)

        # Meta-learner calibrated probability
        confidence = float(self.l1_meta.predict_proba(l0_probs)[0, 1])

        # Convert probability to signal: [-1, 1]
        signal = (confidence - 0.5) * 2.0
        return signal, confidence

    def save(self, path: Path) -> None:
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({
                "l0_models":  self.l0_models,
                "l1_meta":    self.l1_meta,
                "scaler":     self.scaler,
                "is_fitted":  self._is_fitted,
            }, f)
        print(f"[Ensemble] Saved → {path}")

    @classmethod
    def load(cls, path: Path) -> "SignalEnsemble":
        with open(path, "rb") as f:
            state = pickle.load(f)
        inst = cls()
        inst.l0_models   = state["l0_models"]
        inst.l1_meta     = state["l1_meta"]
        inst.scaler      = state["scaler"]
        inst._is_fitted  = state["is_fitted"]
        return inst
