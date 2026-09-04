"""
tests/test_feature_matrix.py
==============================
Unit tests for the Python FeatureMatrix fallback.
Validates correctness of all 13 features and sequence builder.
No Alpaca API calls — fully offline.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.features.feature_matrix import (
    FeatureMatrix, build_sequences, compute_single,
    bars_from_alpaca, N_FEATURES, FEATURE_NAMES,
)


def make_bars(n: int = 60, start_price: float = 400.0) -> list:
    """Generate synthetic monotonic bar list."""
    rng  = np.random.default_rng(42)
    bars = []
    S    = start_price
    for i in range(n):
        ret = rng.normal(0.0003, 0.012)
        S  *= math.exp(ret)
        bars.append({
            "close":  round(S, 2),
            "open":   round(S * 0.999, 2),
            "high":   round(S * 1.005, 2),
            "low":    round(S * 0.995, 2),
            "volume": float(rng.integers(5_000_000, 50_000_000)),
        })
    return bars


class TestFeatureMatrix:
    def test_output_shape(self):
        fm   = FeatureMatrix()
        bars = make_bars(30)
        for b in bars:
            fm.update(b)
        v = fm.latest()
        assert v.shape == (N_FEATURES,), f"Expected ({N_FEATURES},), got {v.shape}"
        assert v.dtype == np.float32

    def test_n_features_constant(self):
        assert N_FEATURES == 13
        assert len(FEATURE_NAMES) == 13

    def test_insufficient_data_returns_zeros(self):
        fm = FeatureMatrix()
        fm.update({"close": 100.0, "volume": 1e6})
        v  = fm.latest()
        assert v.shape == (N_FEATURES,)
        # With only 1 bar, most features should be zero
        assert v[0] == 0.0  # ret1 requires 2 bars

    def test_returns_correct_sign(self):
        """A rising price should give positive returns."""
        fm = FeatureMatrix()
        for price in [100, 101, 102, 103, 104, 110]:
            fm.update({"close": float(price), "volume": 1e6})
        v = fm.latest()
        assert v[0] > 0   # ret1 positive
        assert v[2] > 0   # ret20 positive (rising from 100 to 110)

    def test_sma_ratio_direction(self):
        """Price above SMA should give positive sma_ratio."""
        fm = FeatureMatrix()
        # Feed 25 bars rising sharply at the end
        for i in range(20):
            fm.update({"close": 100.0, "volume": 1e6})
        for i in range(5):
            fm.update({"close": 120.0, "volume": 1e6})  # well above SMA
        v = fm.latest()
        assert v[3] > 0, "sma_r20 should be positive when price > SMA"

    def test_rv_non_negative(self):
        fm = FeatureMatrix()
        for b in make_bars(30):
            fm.update(b)
        v = fm.latest()
        assert v[5] >= 0, "RV20 must be non-negative"

    def test_iv_rank_bounds(self):
        fm = FeatureMatrix()
        for b in make_bars(60):
            fm.update(b)
        v = fm.latest()
        assert 0.0 <= v[7] <= 100.0, f"IV Rank out of [0,100]: {v[7]}"

    def test_vol_ratio_non_negative(self):
        fm = FeatureMatrix()
        for b in make_bars(30):
            fm.update(b)
        v = fm.latest()
        assert v[12] >= 0, "Volume ratio must be non-negative"

    def test_greeks_update(self):
        fm = FeatureMatrix()
        fm.set_greeks(delta=-0.35, gamma=0.04, theta=-0.02, vega=0.12)
        for b in make_bars(5):
            fm.update(b)
        v = fm.latest()
        assert v[8]  == pytest.approx(-0.35, abs=0.01)  # avg_delta
        assert v[9]  == pytest.approx(0.04,  abs=0.01)  # avg_gamma
        assert v[10] == pytest.approx(-0.02, abs=0.01)  # avg_theta
        assert v[11] == pytest.approx(0.12,  abs=0.01)  # avg_vega

    def test_clip_extreme_values(self):
        """Pathological data (stock halted at $0) should not produce NaN."""
        fm = FeatureMatrix()
        fm.update({"close": 100.0, "volume": 1e6})
        fm.update({"close": 0.001, "volume": 0})   # dramatic price drop
        fm.update({"close": 100.0, "volume": 1e6})
        v = fm.latest()
        assert not np.any(np.isnan(v)), "NaN in feature vector"
        assert not np.any(np.isinf(v)), "Inf in feature vector"


class TestBuildSequences:
    def test_output_shape(self):
        bars = make_bars(60)
        seqs = build_sequences(bars, lookback=20)
        assert seqs.ndim == 3
        assert seqs.shape[1] == 20
        assert seqs.shape[2] == N_FEATURES

    def test_minimum_sequences(self):
        bars = make_bars(40)
        seqs = build_sequences(bars, lookback=20)
        assert len(seqs) >= 1

    def test_raises_on_insufficient_bars(self):
        bars = make_bars(10)
        with pytest.raises(ValueError):
            build_sequences(bars, lookback=20)

    def test_dtype_float32(self):
        seqs = build_sequences(make_bars(40), lookback=20)
        assert seqs.dtype == np.float32

    def test_no_nan_in_sequences(self):
        seqs = build_sequences(make_bars(60), lookback=20)
        assert not np.any(np.isnan(seqs))


class TestComputeSingle:
    def test_correct_shape(self):
        bars = make_bars(30)
        v    = compute_single(bars)
        assert v.shape == (N_FEATURES,)

    def test_with_iv_series(self):
        bars = make_bars(30)
        ivs  = [0.20 + 0.001 * i for i in range(len(bars))]
        v    = compute_single(bars, iv_series=ivs)
        assert v.shape == (N_FEATURES,)
        assert v[6] > 0   # iv should be non-zero


class TestBarsFromAlpaca:
    def test_dict_format(self):
        raw = [{"close": 410.5, "volume": 8e7, "open": 409.0, "high": 412.0, "low": 408.0}]
        out = bars_from_alpaca(raw)
        assert out[0]["close"] == pytest.approx(410.5)

    def test_short_key_format(self):
        raw = [{"c": 410.5, "v": 8e7, "o": 409.0, "h": 412.0, "l": 408.0}]
        out = bars_from_alpaca(raw)
        assert out[0]["close"] == pytest.approx(410.5)
