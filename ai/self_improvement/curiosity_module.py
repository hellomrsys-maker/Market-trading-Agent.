"""
ai/self_improvement/curiosity_module.py
========================================
OptionAlpha Agent — Random Network Distillation (RND) Curiosity Module

Provides intrinsic exploration rewards for Reinforcement Learning (PPO).
Prevents policy collapse onto a narrow subset of strikes/DTEs by rewarding
the agent for exploring novel market feature spaces and volatility states.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np


class RNDCuriosityModule(nn.Module):
    """
    Random Network Distillation intrinsic motivation generator.
    """

    def __init__(self, state_dim: int, hidden_dim: int = 64, lr: float = 1e-3):
        super().__init__()
        self.state_dim = state_dim

        # 1. Target Network (Fixed random weights, never trained)
        self.target = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )
        for param in self.target.parameters():
            param.requires_grad = False

        # 2. Predictor Network (Trained to predict target output)
        self.predictor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )

        self.optimizer = optim.Adam(self.predictor.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

    def compute_intrinsic_reward(self, state: np.ndarray) -> float:
        """
        Calculates MSE prediction error as intrinsic reward.
        High error = novel state = high curiosity reward.
        """
        self.eval()
        with torch.no_grad():
            x = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
            target_feat = self.target(x)
            pred_feat = self.predictor(x)
            error = torch.mean((pred_feat - target_feat) ** 2).item()

        # Clip intrinsic reward to avoid destabilizing extrinsic P&L gradient
        return float(min(1.0, error * 10.0))

    def update(self, states: torch.Tensor) -> float:
        """
        Trains predictor on visited batch of states.
        """
        self.train()
        self.optimizer.zero_grad()
        target_feat = self.target(states)
        pred_feat = self.predictor(states)
        loss = self.loss_fn(pred_feat, target_feat)
        loss.backward()
        self.optimizer.step()
        return loss.item()
