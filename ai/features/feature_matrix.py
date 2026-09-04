"""
ai/features/feature_matrix.py
===============================
OptionAlpha Agent — Python Feature Matrix (Fallback)

Pure-Python implementation of the 13-feature vector that mirrors the
Rust FeatureMatrix extension. Used automatically when the Rust
`optionalpha_data` PyO3 extension is not compiled.

Features (in order, matching FEATURE_NAMES in signal_ensemble.py):
  0  close_ret_1   — 1-day log return
  1  close_ret_5   — 5-day log return
  2  close_ret_20  — 20-day log return (momentum)
  3  sma_r20       — (close / SMA-20) - 1   (price deviation from 20-day MA)
  4  sma_r50       — (close / SMA-50) - 1   (price deviation from 50-day MA)
  5  rv20          — 20-day realised vol (annualised)
  6  iv            — ATM implied volatility (from snapshot; fallback = rv20*1.1)
  7  iv_rank       — IV Rank 0–100 (percentile of IV over past 252 days)
  8  avg_delta     — avg absolute delta of open option positions
  9  avg_gamma     — avg gamma
  10 avg_theta     — avg theta (negative)
  11 avg_vega      — avg vega
  12 vol_ratio     — today's volume / 20-day avg volume

The Rust engine computes the same 13 features with sub-millisecond
latency. This Python version is ~50× slower but functionally identical.
It is used during:
  - AI training (offline, latency-insensitive)
  - Development / testing (no Rust toolchain required)
  - CI environments

Usage:
    from ai.features.feature_matrix import FeatureMatrix, build_sequences

    fm      = FeatureMatrix()
    bars    = [{"close": 412.5, "volume": 8e7, ...}, ...]   # OHLCV dicts
    vector  = fm.compute(bars)          # (13,) numpy array, latest bar
    seqs    = build_sequences(bars, lookback=20)  # (N, 20, 13) for Transformer
"""

from __future__ import annotations

import math
from collections import deque
from typing import Dict, List, Optional, Sequence

import numpy as np

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
N_FEATURES   = 13
LOOKBACK_MAX = 252      # max bars kept in rolling window
IV_MULT      = 1.10     # IV ≈ RV × 1.10 when real IV data unavailable
ANNUALISE    = math.sqrt(252)

FEATURE_NAMES = [
    "close_ret_1", "close_ret_5", "close_ret_20",
    "sma_r20", "sma_r50",
    "rv20", "iv", "iv_rank",
    "avg_delta", "avg_gamma", "avg_theta", "avg_vega",
    "vol_ratio",
]


class FeatureMatrix:
    """
    Online (streaming) feature computer. Feed one bar at a time with
    `update()`, then call `latest()` to get the current 13-dim vector.

    Thread safety: NOT thread-safe. Use one instance per symbol.
    """

    def __init__(self):
        self._closes:  deque = deque(maxlen=LOOKBACK_MAX)
        self._volumes: deque = deque(maxlen=LOOKBACK_MAX)
        self._iv_hist: deque = deque(maxlen=LOOKBACK_MAX)  # for IV Rank

        # Portfolio-level Greeks (set externally from option snapshots)
        self.avg_delta: float = 0.0
        self.avg_gamma: float = 0.0
        self.avg_theta: float = 0.0
        self.avg_vega:  float = 0.0

    def update(self, bar: Dict, iv: Optional[float] = None) -> None:
        """
        Ingest one OHLCV bar dict:
          bar = {"close": float, "volume": float, ...}
        iv: ATM implied volatility (optional; will estimate from RV if omitted)
        """
        close  = float(bar["close"])
        volume = float(bar.get("volume", 0))
        self._closes.append(close)
        self._volumes.append(volume)
        # Estimate IV from realised vol if not provided
        iv_val = iv if iv is not None else self._rv(20) * IV_MULT
        self._iv_hist.append(iv_val)

    def latest(self) -> np.ndarray:
        """Return the current 13-dim feature vector as float32."""
        n = len(self._closes)
        if n < 2:
            return np.zeros(N_FEATURES, dtype=np.float32)

        closes  = np.array(self._closes, dtype=np.float64)
        volumes = np.array(self._volumes, dtype=np.float64)

        c = closes[-1]

        # ── Returns ──────────────────────────────────────────
        ret1  = math.log(c / closes[-2]) if n >= 2  else 0.0
        ret5  = math.log(c / closes[-6]) if n >= 6  else ret1 * 5
        ret20 = math.log(c / closes[-21]) if n >= 21 else ret1 * 20

        # ── Moving averages ───────────────────────────────────
        sma20 = closes[-20:].mean()  if n >= 20 else closes.mean()
        sma50 = closes[-50:].mean()  if n >= 50 else closes.mean()
        sma_r20 = c / sma20 - 1.0
        sma_r50 = c / sma50 - 1.0

        # ── Realised volatility (20-day) ──────────────────────
        rv20 = self._rv(20)

        # ── IV and IV Rank ────────────────────────────────────
        iv     = float(self._iv_hist[-1])
        iv_rank = self._iv_rank()

        # ── Volume ratio ──────────────────────────────────────
        avg_vol  = volumes[-20:].mean() if n >= 20 else volumes.mean()
        vol_ratio = float(volumes[-1]) / max(avg_vol, 1.0)

        feats = np.array([
            ret1, ret5, ret20,
            sma_r20, sma_r50,
            rv20, iv, iv_rank,
            self.avg_delta, self.avg_gamma, self.avg_theta, self.avg_vega,
            vol_ratio,
        ], dtype=np.float32)

        # Clip extreme values (handles bad ticks / data gaps)
        feats = np.clip(feats, -10.0, 10.0)
        return feats

    def set_greeks(self, delta: float, gamma: float, theta: float, vega: float) -> None:
        """Update portfolio-level Greeks from the latest option snapshot."""
        self.avg_delta = delta
        self.avg_gamma = gamma
        self.avg_theta = theta
        self.avg_vega  = vega

    # ─────────────────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────────────────
    def _rv(self, window: int) -> float:
        """Annualised realised volatility over `window` bars."""
        closes = list(self._closes)
        if len(closes) < window + 1:
            closes_arr = np.array(closes, dtype=np.float64)
        else:
            closes_arr = np.array(closes[-(window + 1):], dtype=np.float64)

        if len(closes_arr) < 2:
            return 0.20   # default 20% vol
        log_rets = np.diff(np.log(closes_arr))
        return float(log_rets.std() * ANNUALISE)

    def _iv_rank(self) -> float:
        """
        IV Rank = (current_IV - min_IV_252) / (max_IV_252 - min_IV_252) × 100
        Returns value in [0, 100].
        """
        ivs = list(self._iv_hist)
        if len(ivs) < 5:
            return 50.0
        arr     = np.array(ivs, dtype=np.float64)
        lo, hi  = arr.min(), arr.max()
        current = arr[-1]
        if hi <= lo:
            return 50.0
        return float(np.clip((current - lo) / (hi - lo) * 100, 0, 100))


# ─────────────────────────────────────────────────────────────
# Batch builder
# ─────────────────────────────────────────────────────────────

def compute_single(bars: Sequence[Dict], iv_series: Optional[List[float]] = None) -> np.ndarray:
    """
    Compute features for the *latest* bar in a bar list.
    bars: list of OHLCV dicts in chronological order.
    Returns (13,) float32 array.
    """
    fm = FeatureMatrix()
    for i, bar in enumerate(bars):
        iv = iv_series[i] if iv_series and i < len(iv_series) else None
        fm.update(bar, iv)
    return fm.latest()


def build_sequences(
    bars:       Sequence[Dict],
    lookback:   int   = 20,
    iv_series:  Optional[List[float]] = None,
    step:       int   = 1,
) -> np.ndarray:
    """
    Build a (N, lookback, 13) array of overlapping sliding windows.
    Used to generate training sequences for the Regime Transformer.

    bars:     full history in chronological order (≥ lookback + 1 bars)
    lookback: window size (default 20 trading days)
    step:     stride between windows (1 = maximum overlap)
    """
    n = len(bars)
    if n < lookback + 1:
        raise ValueError(f"Need at least {lookback + 1} bars, got {n}")

    # Pre-compute ALL feature vectors
    fm = FeatureMatrix()
    all_features: List[np.ndarray] = []
    for i, bar in enumerate(bars):
        iv = iv_series[i] if iv_series and i < len(iv_series) else None
        fm.update(bar, iv)
        if len(fm._closes) >= 2:
            all_features.append(fm.latest())
        else:
            all_features.append(np.zeros(N_FEATURES, dtype=np.float32))

    # Slice into overlapping windows
    sequences = []
    for end in range(lookback, len(all_features), step):
        window = all_features[end - lookback: end]
        if len(window) == lookback:
            sequences.append(np.stack(window))   # (lookback, 13)

    return np.array(sequences, dtype=np.float32)   # (N, lookback, 13)


def bars_from_alpaca(raw_bars: List[Dict]) -> List[Dict]:
    """
    Normalise Alpaca bar objects (or dicts) to the standard format
    expected by FeatureMatrix: {"close": float, "volume": float}.
    """
    out = []
    for b in raw_bars:
        if hasattr(b, "close"):
            # alpaca-py Bar object
            out.append({"close": float(b.close), "volume": float(b.volume or 0),
                        "open": float(b.open), "high": float(b.high), "low": float(b.low)})
        else:
            out.append({
                "close":  float(b.get("close", b.get("c", 0))),
                "volume": float(b.get("volume", b.get("v", 0))),
                "open":   float(b.get("open",   b.get("o", 0))),
                "high":   float(b.get("high",   b.get("h", 0))),
                "low":    float(b.get("low",    b.get("l", 0))),
            })
    return out
