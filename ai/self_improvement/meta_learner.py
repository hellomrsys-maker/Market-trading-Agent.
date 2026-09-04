"""
ai/self_improvement/meta_learner.py
====================================
OptionAlpha Agent — Fast Adaptation Meta-Learner (MAML Style)

Enables rapid 5-step fine-tuning when the Regime Transformer detects a sustained macro regime shift.
Only updates the classification head layers, preserving the base feature representations.
"""

from __future__ import annotations

import copy
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from loguru import logger

from ai.transformer.regime_detector import RegimeDetector, LOOKBACK, N_FEATURES


class FastAdaptationMetaLearner:
    """
    Rapid fine-tuning module for regime-specific model specialization.
    """

    def __init__(self, base_model: RegimeDetector, inner_lr: float = 1e-3):
        self.model = base_model
        self.inner_lr = inner_lr

    def adapt_to_new_regime(
        self,
        support_sequences: List[np.ndarray],
        target_regime_id: int,
        steps: int = 5,
    ) -> RegimeDetector:
        """
        Takes 5-10 support samples from a newly emerging market regime,
        and performs rapid inner-loop gradient adaptation on the top layers.
        """
        if len(support_sequences) == 0:
            return self.model

        adapted_model = copy.deepcopy(self.model)
        adapted_model.train()

        # Freeze lower embedding layers, fine-tune only transformer encoder top and head
        optimizer = optim.Adam(
            [p for p in adapted_model.head.parameters()] +
            [p for p in adapted_model.encoder.layers[-1].parameters()],
            lr=self.inner_lr
        )
        loss_fn = nn.CrossEntropyLoss()

        X = torch.as_tensor(np.stack(support_sequences), dtype=torch.float32)
        y = torch.full((len(support_sequences),), target_regime_id, dtype=torch.long)

        for step in range(steps):
            optimizer.zero_grad()
            logits = adapted_model(X)
            loss = loss_fn(logits, y)
            loss.backward()
            optimizer.step()

        logger.info("FastAdaptation: Adapted model to regime {} in {} steps (loss: {:.4f})", target_regime_id, steps, loss.item())
        return adapted_model
