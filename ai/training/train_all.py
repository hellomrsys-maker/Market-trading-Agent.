"""
ai/training/train_all.py
=========================
OptionAlpha Agent — Unified AI Training Pipeline

Trains all three self-developed models in sequence:
  1. Regime Transformer   — market regime classifier (285K params)
  2. PPO RL Agent         — options trading decision maker
  3. Signal Ensemble      — XGBoost + LightGBM + CatBoost confidence gate

Run this ONCE before starting the live agent (or when you want to retrain):
    python -m ai.training.train_all
    python -m ai.training.train_all --device cuda --epochs 300 --symbols SPY QQQ AAPL

Training output (all saved to data/models/):
    regime_detector_best.pt   — best Transformer checkpoint
    ppo_agent_latest.pt       — latest PPO weights
    ppo_agent_latest.onnx     — ONNX export for runtime inference
    signal_ensemble.pkl       — fitted stacked ensemble
    training_report.json      — metrics for every model
    training_report.md        — human-readable training summary

Pipeline:
    DataCollector.collect_all()
        → build_sequences()        (ai/features/feature_matrix.py)
        → RegimeTrainer.train()    (ai/transformer/regime_detector.py)
        → PPOTrainer.train()       (ai/rl/ppo_agent.py)
        → SignalEnsemble.fit()     (ai/ensemble/signal_ensemble.py)
        → save_report()
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from loguru import logger


# ─────────────────────────────────────────────────────────────
# Training pipeline
# ─────────────────────────────────────────────────────────────

class TrainingPipeline:

    def __init__(
        self,
        symbols:   List[str],
        device:    str   = "cpu",
        epochs:    int   = 200,
        rl_steps:  int   = 500_000,
        model_dir: Path  = Path("data/models"),
        cache_dir: Path  = Path("data/cache"),
        skip_collect: bool = False,
    ):
        self.symbols      = symbols
        self.device       = device
        self.epochs       = epochs
        self.rl_steps     = rl_steps
        self.model_dir    = Path(model_dir)
        self.cache_dir    = Path(cache_dir)
        self.skip_collect = skip_collect
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.report: Dict = {"started_at": datetime.now().isoformat(), "models": {}}

    # ─────────────────────────────────────────────────────────
    # Step 0: Data collection
    # ─────────────────────────────────────────────────────────
    def collect_data(self) -> List[np.ndarray]:
        """Download bars, build feature sequences. Returns list of (20,13) arrays."""
        if self.skip_collect:
            logger.info("Skipping data collection (--skip-collect)")
        else:
            logger.info("Step 0/3 — Collecting historical data for: {}", self.symbols)
            from data.collector import DataCollector
            dc = DataCollector()
            results = dc.collect_all(symbols=self.symbols, days=504)
            logger.info("Collection results: {}", results)

        # Load pre-built sequences
        seq_path = self.cache_dir / "all_sequences.json"
        if seq_path.exists():
            raw = json.loads(seq_path.read_text())
            seqs = [np.array(s, dtype=np.float32) for s in raw if len(s) == 20]
            logger.info("Loaded {} sequences from cache (shape per seq: 20×13)", len(seqs))
        else:
            # Fallback: build on-the-fly from synthetic data
            logger.warning("No sequence cache — building synthetic sequences for training")
            from data.collector import DataCollector
            from ai.features.feature_matrix import build_sequences, bars_from_alpaca
            dc   = DataCollector()
            seqs = []
            for sym in self.symbols:
                bars = dc._synthetic_bars(sym, 504)
                std  = bars_from_alpaca(bars)
                s    = build_sequences(std, lookback=20)
                seqs.extend(s)
            seqs = [np.array(s, dtype=np.float32) for s in seqs]
            logger.info("Built {} synthetic sequences", len(seqs))

        if len(seqs) < 50:
            logger.warning("Very few sequences ({}) — results may be poor", len(seqs))
        return seqs

    # ─────────────────────────────────────────────────────────
    # Step 1: Regime Transformer
    # ─────────────────────────────────────────────────────────
    def train_transformer(self, sequences: List[np.ndarray]) -> Dict:
        logger.info("=" * 55)
        logger.info("Step 1/3 — Training Regime Transformer")
        logger.info("  Sequences: {} | Epochs: {} | Device: {}", len(sequences), self.epochs, self.device)

        t0 = time.time()
        from ai.transformer.regime_detector import RegimeDetector, RegimeTrainer

        model   = RegimeDetector()
        trainer = RegimeTrainer(model, device=self.device)
        history = trainer.train(
            sequences      = sequences,
            epochs         = self.epochs,
            checkpoint_dir = self.model_dir,
        )

        elapsed = time.time() - t0
        best_acc = max(history["val_acc"]) if history["val_acc"] else 0.0
        n_params = model.count_params()

        metrics = {
            "model":         "RegimeTransformer",
            "n_params":      n_params,
            "n_sequences":   len(sequences),
            "epochs_run":    len(history["train_loss"]),
            "best_val_acc":  round(best_acc, 4),
            "final_loss":    round(history["train_loss"][-1], 6) if history["train_loss"] else 0,
            "train_time_s":  round(elapsed, 1),
            "checkpoint":    str(self.model_dir / "regime_detector_best.pt"),
        }

        logger.success("Transformer trained | val_acc={:.3f} | params={:,} | {:.0f}s",
                       best_acc, n_params, elapsed)
        return metrics

    # ─────────────────────────────────────────────────────────
    # Step 2: PPO RL Agent
    # ─────────────────────────────────────────────────────────
    def train_ppo(self) -> Dict:
        logger.info("=" * 55)
        logger.info("Step 2/3 — Training PPO RL Agent")
        logger.info("  Timesteps: {:,} | Device: {}", self.rl_steps, self.device)

        t0 = time.time()

        from ai.rl.trading_env import OptionsPortfolioEnv, OBS_DIM, N_ACTIONS
        from ai.rl.ppo_agent import PPOTrainer

        # Point env at data cache
        env     = OptionsPortfolioEnv(data_dir=self.cache_dir)
        trainer = PPOTrainer(OBS_DIM, N_ACTIONS, device=self.device)

        history = trainer.train(
            env            = env,
            total_timesteps= self.rl_steps,
            checkpoint_dir = self.model_dir,
        )

        # Export ONNX
        onnx_path = self.model_dir / "ppo_agent_latest.onnx"
        try:
            trainer.export_onnx(onnx_path, OBS_DIM)
            logger.info("ONNX exported → {}", onnx_path)
        except Exception as exc:
            logger.warning("ONNX export failed: {}", exc)

        elapsed = time.time() - t0
        ep_rewards = history.get("episode_rewards", [0])
        metrics = {
            "model":             "PPO_RLAgent",
            "obs_dim":           OBS_DIM,
            "n_actions":         N_ACTIONS,
            "total_timesteps":   self.rl_steps,
            "n_episodes":        len(ep_rewards),
            "mean_ep_reward":    round(float(np.mean(ep_rewards[-20:])), 6) if ep_rewards else 0,
            "max_ep_reward":     round(float(np.max(ep_rewards)), 6) if ep_rewards else 0,
            "final_entropy":     round(history["entropy"][-1], 4) if history.get("entropy") else 0,
            "train_time_s":      round(elapsed, 1),
            "checkpoint_pt":     str(self.model_dir / "ppo_agent_latest.pt"),
            "checkpoint_onnx":   str(onnx_path),
        }

        logger.success("PPO trained | mean_ep_rw={:.4f} | {} episodes | {:.0f}s",
                       metrics["mean_ep_reward"], len(ep_rewards), elapsed)
        return metrics

    # ─────────────────────────────────────────────────────────
    # Step 3: Signal Ensemble
    # ─────────────────────────────────────────────────────────
    def train_ensemble(self, sequences: List[np.ndarray]) -> Dict:
        logger.info("=" * 55)
        logger.info("Step 3/3 — Training Signal Ensemble")

        t0 = time.time()
        from ai.ensemble.signal_ensemble import SignalEnsemble

        # Use last-bar features from each sequence (N, 13)
        X = np.stack([s[-1] for s in sequences], axis=0).astype(np.float32)

        # Build approximate returns from 20-day momentum feature (index 2)
        returns = X[:, 2].copy()  # close_ret_20 as proxy for forward return

        # Pad to 23 features (add zeros for order flow + regime + account)
        pad = np.zeros((len(X), 10), dtype=np.float32)
        X23 = np.concatenate([X, pad], axis=1)

        ensemble = SignalEnsemble()
        metrics_dict = ensemble.fit(X23, returns)

        # Save
        save_path = self.model_dir / "signal_ensemble.pkl"
        ensemble.save(save_path)

        elapsed = time.time() - t0
        metrics = {
            "model":        "SignalEnsemble",
            "n_samples":    len(X),
            "n_features":   23,
            "model_aucs":   {k: round(v, 4) for k, v in metrics_dict.items()},
            "train_time_s": round(elapsed, 1),
            "checkpoint":   str(save_path),
        }
        logger.success("Ensemble trained | AUCs={} | {:.0f}s", metrics_dict, elapsed)
        return metrics

    # ─────────────────────────────────────────────────────────
    # Report
    # ─────────────────────────────────────────────────────────
    def save_report(self) -> None:
        self.report["completed_at"] = datetime.now().isoformat()
        self.report["symbols"]      = self.symbols
        self.report["device"]       = self.device

        # JSON
        json_path = self.model_dir / "training_report.json"
        json_path.write_text(json.dumps(self.report, indent=2))

        # Markdown
        md_lines = [
            "# OptionAlpha Agent — Training Report",
            f"\n**Completed:** {self.report['completed_at']}",
            f"**Symbols:** {', '.join(self.symbols)}",
            f"**Device:** {self.device}\n",
            "---\n",
        ]
        for name, m in self.report.get("models", {}).items():
            md_lines.append(f"## {name}\n")
            for k, v in m.items():
                md_lines.append(f"- **{k}**: `{v}`")
            md_lines.append("")

        md_path = self.model_dir / "training_report.md"
        md_path.write_text("\n".join(md_lines))
        logger.info("Training report saved → {}", md_path)

    # ─────────────────────────────────────────────────────────
    # Full pipeline
    # ─────────────────────────────────────────────────────────
    def run(self) -> Dict:
        logger.info("OptionAlpha Training Pipeline")
        logger.info("Symbols: {} | Device: {} | Epochs: {}", self.symbols, self.device, self.epochs)

        sequences = self.collect_data()

        m1 = self.train_transformer(sequences)
        self.report["models"]["RegimeTransformer"] = m1

        m2 = self.train_ppo()
        self.report["models"]["PPO_RLAgent"] = m2

        m3 = self.train_ensemble(sequences)
        self.report["models"]["SignalEnsemble"] = m3

        self.save_report()
        logger.success("All models trained. Ready to run: python run_agent.py")
        return self.report


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train all OptionAlpha AI models")
    p.add_argument("--symbols",      nargs="+", default=None,
                   help="Symbols to collect/train on (default: all universe)")
    p.add_argument("--device",       default="auto",
                   choices=["auto", "cpu", "cuda", "mps"])
    p.add_argument("--epochs",       type=int, default=200,
                   help="Transformer training epochs")
    p.add_argument("--rl-steps",     type=int, default=500_000,
                   help="PPO total environment timesteps")
    p.add_argument("--skip-collect", action="store_true",
                   help="Skip data collection (use existing cache)")
    p.add_argument("--model-dir",    default="data/models")
    return p.parse_args()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from dotenv import load_dotenv
    load_dotenv()

    args = parse_args()

    # Resolve device
    device = args.device
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"

    from config.settings import get_strategy_settings
    symbols = args.symbols or get_strategy_settings().trading_universe

    pipeline = TrainingPipeline(
        symbols      = symbols,
        device       = device,
        epochs       = args.epochs,
        rl_steps     = args.rl_steps,
        model_dir    = Path(args.model_dir),
        skip_collect = args.skip_collect,
    )
    report = pipeline.run()
    print(f"\n✅ Training complete. Report: {Path(args.model_dir) / 'training_report.md'}")
