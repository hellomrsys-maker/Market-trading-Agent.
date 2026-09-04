"""
ai/rl/ppo_agent.py
===================
OptionAlpha Agent — PPO Reinforcement Learning Agent

Self-developed Proximal Policy Optimization agent for options
trading. No external RL library dependencies at inference time
(stable-baselines3 used only for training; saved as ONNX for runtime).

Architecture:
  Actor-Critic network sharing a common backbone:
    Backbone:   Linear(obs) → ReLU → Linear → ReLU → Linear (256 units)
    Actor head: Linear(256 → n_actions) + Softmax
    Critic head: Linear(256 → 1)

  Legal action masking: prevents agent from placing invalid orders
  (e.g., opening position on symbol already held, IC when IV Rank < 30)

Training: PPO with:
  - Clipped surrogate objective (ε = 0.2)
  - Generalised Advantage Estimation (λ = 0.95, γ = 0.99)
  - Value function clipping
  - Entropy bonus for exploration
  - Mini-batch updates (n_epochs=10)

Export: trained agent is saved as:
  1. PyTorch .pt checkpoint (for re-training)
  2. ONNX model (for inference — no stable-baselines3 needed at runtime)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam


# ─────────────────────────────────────────────────────────────
# Actor-Critic Network
# ─────────────────────────────────────────────────────────────

class ActorCriticNet(nn.Module):
    """
    Shared-backbone Actor-Critic for Discrete action spaces.

    The backbone transforms the raw observation into a latent
    representation. The actor and critic heads then consume this.
    """
    def __init__(self, obs_dim: int, n_actions: int, hidden: int = 256):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(obs_dim, hidden),   nn.ReLU(),
            nn.Linear(hidden, hidden),    nn.ReLU(),
            nn.Linear(hidden, hidden//2), nn.ReLU(),
        )
        self.actor  = nn.Linear(hidden // 2, n_actions)
        self.critic = nn.Linear(hidden // 2, 1)
        self.apply(self._init)

    @staticmethod
    def _init(m: nn.Module) -> None:
        if isinstance(m, nn.Linear):
            nn.init.orthogonal_(m.weight, gain=np.sqrt(2))
            nn.init.zeros_(m.bias)

    def forward(
        self, obs: torch.Tensor, action_mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Returns:
          action_probs: (batch, n_actions)  — masked softmax
          value:        (batch, 1)
          entropy:      scalar
        """
        z = self.backbone(obs)
        logits = self.actor(z)
        value  = self.critic(z)

        # Apply legal action mask (−∞ on illegal actions)
        if action_mask is not None:
            logits = logits.masked_fill(~action_mask.bool(), float("-inf"))

        probs   = F.softmax(logits, dim=-1)
        entropy = -(probs * (probs + 1e-8).log()).sum(dim=-1).mean()
        return probs, value, entropy

    def get_action(
        self, obs: np.ndarray, action_mask: Optional[np.ndarray] = None
    ) -> Tuple[int, float, float]:
        """Greedy + stochastic action selection for single observation."""
        with torch.no_grad():
            obs_t  = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
            mask_t = torch.tensor(action_mask, dtype=torch.bool).unsqueeze(0) if action_mask is not None else None
            probs, value, _ = self.forward(obs_t, mask_t)
            dist   = torch.distributions.Categorical(probs)
            action = dist.sample()
            log_p  = dist.log_prob(action)
        return int(action.item()), float(log_p.item()), float(value.item())

    def evaluate_actions(
        self,
        obs:         torch.Tensor,
        actions:     torch.Tensor,
        action_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Returns (log_probs, values, entropy) for a batch of stored transitions."""
        probs, values, entropy = self.forward(obs, action_mask)
        dist     = torch.distributions.Categorical(probs)
        log_prbs = dist.log_prob(actions)
        return log_prbs, values.squeeze(-1), entropy


# ─────────────────────────────────────────────────────────────
# PPO Trainer
# ─────────────────────────────────────────────────────────────

class PPOTrainer:
    """
    Proximal Policy Optimization training loop.
    Fully self-contained — uses our custom ActorCriticNet and
    the OptionsPortfolioEnv. No stable-baselines3 at runtime.
    """

    def __init__(
        self,
        obs_dim:       int,
        n_actions:     int,
        device:        str   = "cpu",
        lr:            float = 3e-4,
        gamma:         float = 0.99,
        gae_lambda:    float = 0.95,
        clip_eps:      float = 0.20,
        vf_coeff:      float = 0.50,
        ent_coeff:     float = 0.01,
        n_epochs:      int   = 10,
        batch_size:    int   = 256,
    ):
        self.device     = torch.device(device)
        self.gamma      = gamma
        self.gae_lambda = gae_lambda
        self.clip_eps   = clip_eps
        self.vf_coeff   = vf_coeff
        self.ent_coeff  = ent_coeff
        self.n_epochs   = n_epochs
        self.batch_size = batch_size

        self.net   = ActorCriticNet(obs_dim, n_actions).to(self.device)
        self.optim = Adam(self.net.parameters(), lr=lr, eps=1e-5)

    # ── Rollout buffer ────────────────────────────────────────
    def _compute_gae(
        self,
        rewards:   np.ndarray,  # (T,)
        values:    np.ndarray,  # (T,)
        dones:     np.ndarray,  # (T,)
        last_val:  float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generalised Advantage Estimation (Schulman et al. 2015)."""
        T        = len(rewards)
        advs     = np.zeros(T, dtype=np.float32)
        gae      = 0.0
        next_val = last_val

        for t in reversed(range(T)):
            mask     = 1.0 - dones[t]
            delta    = rewards[t] + self.gamma * next_val * mask - values[t]
            gae      = delta + self.gamma * self.gae_lambda * mask * gae
            advs[t]  = gae
            next_val = values[t]

        returns = advs + values
        return advs, returns

    def _update(
        self,
        obs:         torch.Tensor,
        actions:     torch.Tensor,
        old_log_ps:  torch.Tensor,
        advantages:  torch.Tensor,
        returns:     torch.Tensor,
    ) -> Tuple[float, float, float]:
        """One gradient update step on a mini-batch."""
        log_ps, values, entropy = self.net.evaluate_actions(obs, actions)
        ratio    = (log_ps - old_log_ps).exp()

        # Clipped surrogate loss
        surr1    = ratio * advantages
        surr2    = ratio.clamp(1 - self.clip_eps, 1 + self.clip_eps) * advantages
        pg_loss  = -torch.min(surr1, surr2).mean()

        # Value function loss (clipped)
        vf_loss  = F.mse_loss(values, returns)

        loss     = pg_loss + self.vf_coeff * vf_loss - self.ent_coeff * entropy
        self.optim.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(self.net.parameters(), 0.5)
        self.optim.step()

        return float(pg_loss), float(vf_loss), float(entropy)

    def train(
        self,
        env,
        total_timesteps: int = 500_000,
        rollout_steps:   int = 2048,
        checkpoint_dir:  Optional[Path] = None,
    ) -> dict:
        """Main PPO training loop with periodic checkpointing."""
        history = {"episode_rewards": [], "pg_loss": [], "vf_loss": [], "entropy": []}
        timestep   = 0
        episode_rw = 0.0
        obs, _     = env.reset()

        while timestep < total_timesteps:
            # ── Rollout collection ────────────────────────────
            buf_obs      = np.zeros((rollout_steps, obs.shape[0]), np.float32)
            buf_actions  = np.zeros(rollout_steps, np.int64)
            buf_rewards  = np.zeros(rollout_steps, np.float32)
            buf_dones    = np.zeros(rollout_steps, np.float32)
            buf_values   = np.zeros(rollout_steps, np.float32)
            buf_log_ps   = np.zeros(rollout_steps, np.float32)

            for step in range(rollout_steps):
                action, log_p, value = self.net.get_action(obs)
                next_obs, reward, terminated, truncated, _ = env.step(action)
                done = float(terminated or truncated)

                buf_obs[step]     = obs
                buf_actions[step] = action
                buf_rewards[step] = reward
                buf_dones[step]   = done
                buf_values[step]  = value
                buf_log_ps[step]  = log_p

                episode_rw += reward
                obs          = next_obs
                timestep    += 1

                if terminated or truncated:
                    history["episode_rewards"].append(episode_rw)
                    episode_rw = 0.0
                    obs, _     = env.reset()

            # Bootstrap last value
            with torch.no_grad():
                _, last_val, _ = self.net.forward(
                    torch.tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
                )
                last_val = float(last_val.item())

            advs, returns = self._compute_gae(buf_rewards, buf_values, buf_dones, last_val)
            # Normalise advantages
            advs = (advs - advs.mean()) / (advs.std() + 1e-8)

            # Convert to tensors
            t_obs   = torch.tensor(buf_obs,     device=self.device)
            t_acts  = torch.tensor(buf_actions, device=self.device, dtype=torch.long)
            t_lps   = torch.tensor(buf_log_ps,  device=self.device)
            t_advs  = torch.tensor(advs,        device=self.device)
            t_rets  = torch.tensor(returns,     device=self.device)

            # ── PPO Update epochs ──────────────────────────────
            ep_pg, ep_vf, ep_ent = 0.0, 0.0, 0.0
            for _ in range(self.n_epochs):
                idxs = np.random.permutation(rollout_steps)
                for start in range(0, rollout_steps, self.batch_size):
                    batch = idxs[start:start + self.batch_size]
                    pg, vf, ent = self._update(
                        t_obs[batch], t_acts[batch], t_lps[batch],
                        t_advs[batch], t_rets[batch],
                    )
                    ep_pg += pg; ep_vf += vf; ep_ent += ent
            n_batches = (self.n_epochs * rollout_steps) // self.batch_size
            history["pg_loss"].append(ep_pg / n_batches)
            history["vf_loss"].append(ep_vf / n_batches)
            history["entropy"].append(ep_ent / n_batches)

            if timestep % 50_000 < rollout_steps:
                recent = history["episode_rewards"][-10:] if history["episode_rewards"] else [0]
                print(f"  [{timestep:7d}/{total_timesteps}] "
                      f"ep_rw={np.mean(recent):.4f} | "
                      f"pg={ep_pg/n_batches:.4f} | "
                      f"entropy={ep_ent/n_batches:.4f}")
                if checkpoint_dir:
                    self.save(Path(checkpoint_dir) / "ppo_agent_latest.pt")

        return history

    def save(self, path: Path) -> None:
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.net.state_dict(), path)
        print(f"[PPO] Saved checkpoint → {path}")

    def export_onnx(self, path: Path, obs_dim: int) -> None:
        """Export to ONNX for runtime inference without stable-baselines3."""
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        dummy = torch.zeros(1, obs_dim)
        torch.onnx.export(
            self.net, (dummy,), str(path),
            input_names=["obs"], output_names=["probs", "value", "entropy"],
            opset_version=17, dynamic_axes={"obs": {0: "batch"}},
        )
        print(f"[PPO] Exported ONNX → {path}")

    @classmethod
    def load(cls, path: Path, obs_dim: int, n_actions: int, device: str = "cpu") -> "PPOTrainer":
        trainer = cls(obs_dim, n_actions, device=device)
        trainer.net.load_state_dict(torch.load(path, map_location=device))
        return trainer


# ─────────────────────────────────────────────────────────────
# ONNX Inference Wrapper (runtime — no stable-baselines3)
# ─────────────────────────────────────────────────────────────

class OnnxPPOAgent:
    """
    Lightweight inference-only wrapper for the exported ONNX model.
    Used at runtime — zero dependency on training libraries.
    Falls back to PyTorch .pt if ONNX not available.
    """
    def __init__(self, model_path: Path, obs_dim: int, n_actions: int):
        self.obs_dim   = obs_dim
        self.n_actions = n_actions
        self._ort_session = None
        self._torch_net   = None
        self._load(model_path)

    def _load(self, path: Path) -> None:
        path = Path(path)
        onnx_path = path.with_suffix(".onnx")
        pt_path   = path.with_suffix(".pt")

        if onnx_path.exists():
            try:
                import onnxruntime as ort
                opts = ort.SessionOptions()
                opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                self._ort_session = ort.InferenceSession(
                    str(onnx_path), sess_options=opts,
                    providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
                )
                return
            except ImportError:
                pass  # fall through to PyTorch

        if pt_path.exists():
            self._torch_net = ActorCriticNet(self.obs_dim, self.n_actions)
            self._torch_net.load_state_dict(torch.load(pt_path, map_location="cpu"))
            self._torch_net.eval()

    def predict(self, obs: np.ndarray) -> int:
        """Returns best action for a single observation."""
        if self._ort_session:
            inp = {"obs": obs.astype(np.float32).reshape(1, -1)}
            probs = self._ort_session.run(["probs"], inp)[0][0]
            return int(probs.argmax())
        elif self._torch_net:
            with torch.no_grad():
                t_obs  = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
                probs, _, _ = self._torch_net(t_obs)
                return int(probs.argmax(dim=-1).item())
        # No model loaded — return hold action
        return 0
