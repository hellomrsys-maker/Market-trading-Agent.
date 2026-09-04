"""
tests/test_high_throughput_trainer.py
=====================================
Unit tests for PolyglotHighThroughputTrainer.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.training.high_throughput_trainer import PolyglotHighThroughputTrainer


class TestPolyglotHighThroughputTrainer:
    def test_trainer_initialization(self):
        trainer = PolyglotHighThroughputTrainer(batch_size=16, sequence_length=10)
        assert trainer.regime_detector is not None
        assert trainer.curiosity is not None
        assert trainer.governor is not None

    def test_train_epoch_throughput(self):
        trainer = PolyglotHighThroughputTrainer(batch_size=32, sequence_length=10)
        metrics = trainer.train_epoch(num_batches=2, lr=1e-3)
        assert len(metrics) == 2
        assert metrics[-1].throughput_samples_per_sec > 0.0
        assert metrics[-1].loss >= 0.0
        assert 0.0 <= metrics[-1].regime_accuracy <= 1.0

    def test_co_simulation_cycle(self):
        trainer = PolyglotHighThroughputTrainer(batch_size=16)
        res = trainer.co_simulate_cognitive_day(["SPY", "QQQ"])
        assert res["status"] == "success"
        assert res["zero_bridge_status"] == "ACTIVE_0_NS"
        assert "SPY" in res["decisions"]
        assert "QQQ" in res["decisions"]
