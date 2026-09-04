"""
tests/test_regime_detector.py
==============================
Unit tests for the Regime Transformer model.
No GPU required — CPU-only, no training, just forward-pass validation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.transformer.regime_detector import (
    RegimeDetector, RegimeTrainer,
    N_FEATURES, LOOKBACK, N_REGIMES, D_MODEL,
)


@pytest.fixture
def model() -> RegimeDetector:
    return RegimeDetector()


@pytest.fixture
def dummy_seq() -> np.ndarray:
    """Random (LOOKBACK, N_FEATURES) float32 array."""
    rng = np.random.default_rng(0)
    return rng.standard_normal((LOOKBACK, N_FEATURES)).astype(np.float32)


class TestRegimeDetectorArchitecture:
    def test_param_count(self, model):
        n = model.count_params()
        assert 100_000 < n < 2_000_000, f"Unexpected param count: {n:,}"

    def test_forward_output_shape(self, model):
        x      = torch.randn(4, LOOKBACK, N_FEATURES)
        logits = model(x)
        assert logits.shape == (4, N_REGIMES)

    def test_forward_no_nan(self, model):
        x      = torch.randn(8, LOOKBACK, N_FEATURES)
        logits = model(x)
        assert not torch.any(torch.isnan(logits))
        assert not torch.any(torch.isinf(logits))

    def test_batch_size_one(self, model):
        x      = torch.randn(1, LOOKBACK, N_FEATURES)
        logits = model(x)
        assert logits.shape == (1, N_REGIMES)

    def test_regime_names(self, model):
        assert len(model.REGIME_NAMES) == N_REGIMES
        assert "Neutral" in model.REGIME_NAMES


class TestRegimeDetectorPredict:
    def test_predict_output_types(self, model, dummy_seq):
        regime_id, probs = model.predict(dummy_seq)
        assert isinstance(regime_id, int)
        assert isinstance(probs, np.ndarray)
        assert probs.shape == (N_REGIMES,)

    def test_predict_probs_sum_to_one(self, model, dummy_seq):
        _, probs = model.predict(dummy_seq)
        assert abs(probs.sum() - 1.0) < 1e-5, f"Probs sum={probs.sum()}"

    def test_predict_regime_in_range(self, model, dummy_seq):
        regime_id, _ = model.predict(dummy_seq)
        assert 0 <= regime_id < N_REGIMES

    def test_regime_name_valid(self, model, dummy_seq):
        regime_id, _ = model.predict(dummy_seq)
        name = model.regime_name(regime_id)
        assert name in model.REGIME_NAMES


class TestRegimeDetectorSaveLoad:
    def test_save_load_roundtrip(self, model, dummy_seq, tmp_path):
        pt_path = tmp_path / "test_regime.pt"
        model.save(pt_path)
        assert pt_path.exists()

        loaded = RegimeDetector.load(pt_path, device="cpu")
        rid1, probs1 = model.predict(dummy_seq)
        rid2, probs2 = loaded.predict(dummy_seq)

        assert rid1 == rid2
        np.testing.assert_allclose(probs1, probs2, atol=1e-5)


class TestRegimeTrainer:
    def test_auto_label_high_iv(self):
        trainer = RegimeTrainer(RegimeDetector(), device="cpu")
        seq = np.zeros((LOOKBACK, N_FEATURES), dtype=np.float32)
        seq[-1, 7] = 45.0   # iv_rank > 30 → High-IV
        label = trainer._auto_label(seq)
        assert label == 3

    def test_auto_label_bull(self):
        trainer = RegimeTrainer(RegimeDetector(), device="cpu")
        seq = np.zeros((LOOKBACK, N_FEATURES), dtype=np.float32)
        seq[-1, 7]  = 15.0   # iv_rank < 30
        seq[-1, 2]  = 0.05   # positive momentum
        seq[-1, 4]  = 0.02   # price above sma50
        label = trainer._auto_label(seq)
        assert label == 1

    def test_auto_label_bear(self):
        trainer = RegimeTrainer(RegimeDetector(), device="cpu")
        seq = np.zeros((LOOKBACK, N_FEATURES), dtype=np.float32)
        seq[-1, 7]  = 15.0
        seq[-1, 2]  = -0.05
        seq[-1, 4]  = -0.02
        label = trainer._auto_label(seq)
        assert label == 2

    def test_auto_label_neutral(self):
        trainer = RegimeTrainer(RegimeDetector(), device="cpu")
        seq = np.zeros((LOOKBACK, N_FEATURES), dtype=np.float32)
        label = trainer._auto_label(seq)
        assert label == 0

    def test_train_small_dataset(self):
        """Smoke test: train for 5 epochs on 50 sequences — no error."""
        rng  = np.random.default_rng(1)
        seqs = [rng.standard_normal((LOOKBACK, N_FEATURES)).astype(np.float32)
                for _ in range(50)]

        model   = RegimeDetector()
        trainer = RegimeTrainer(model, device="cpu")
        history = trainer.train(seqs, epochs=5, batch_size=16)

        assert "train_loss" in history
        assert "val_acc"    in history
        assert len(history["train_loss"]) > 0
        assert len(history["val_acc"])    > 0
        # All losses should be finite
        assert all(math.isfinite(l) for l in history["train_loss"])

import math
