"""
data/collector.py
==================
OptionAlpha Agent — Historical Data Collector

Downloads and caches historical market data from Alpaca for:
  1. AI training (Transformer, PPO environment, Ensemble)
  2. IV Rank calculation history (252 trading days of IV)
  3. Option chain snapshots (for feature seeding)

Output files (all in data/cache/):
  bars_{SYMBOL}.parquet     — OHLCV daily bars (2 years)
  features_{SYMBOL}.parquet — Pre-computed 13-dim feature vectors
  historical_features.json  — Serialised episode list for OptionsPortfolioEnv
  iv_history.json           — IV history per symbol for IVRankEngine

Usage:
    # From CLI (standalone):
    python -m data.collector

    # From Python:
    from data.collector import DataCollector
    dc = DataCollector()
    dc.collect_all(symbols=["SPY","QQQ","AAPL"], days=504)
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from loguru import logger

from config.settings import get_alpaca_settings, get_strategy_settings

_cfg_a = get_alpaca_settings()
_cfg_s = get_strategy_settings()

CACHE_DIR = Path(__file__).resolve().parent / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class DataCollector:
    """
    Fetches OHLCV + option data from Alpaca and persists to disk.
    Falls back gracefully when Alpaca is unavailable (uses synthetic data).
    """

    def __init__(self):
        self._trading_client = None
        self._stock_client   = None
        self._opt_client     = None
        self._init_clients()

    def _init_clients(self) -> None:
        try:
            from alpaca.trading.client import TradingClient
            from alpaca.data.historical.stock import StockHistoricalDataClient
            from alpaca.data.historical.option import OptionHistoricalDataClient

            self._trading_client = TradingClient(
                api_key=_cfg_a.api_key, secret_key=_cfg_a.secret_key, paper=True
            )
            self._stock_client = StockHistoricalDataClient(
                api_key=_cfg_a.api_key, secret_key=_cfg_a.secret_key
            )
            self._opt_client = OptionHistoricalDataClient(
                api_key=_cfg_a.api_key, secret_key=_cfg_a.secret_key
            )
            logger.info("DataCollector: Alpaca clients initialised")
        except Exception as exc:
            logger.warning("DataCollector: Alpaca unavailable ({}), will use synthetic data", exc)

    # ─────────────────────────────────────────────────────────
    # Main entry point
    # ─────────────────────────────────────────────────────────

    def collect_all(
        self,
        symbols: Optional[List[str]] = None,
        days:    int = 504,   # ~2 trading years
    ) -> Dict[str, int]:
        """
        Collect OHLCV bars for all universe symbols.
        Returns dict: {symbol: n_bars_collected}.
        """
        symbols = symbols or _cfg_s.trading_universe
        results = {}
        for sym in symbols:
            try:
                bars = self._fetch_bars(sym, days)
                n    = self._save_bars(sym, bars)
                results[sym] = n
                logger.info("Collected {} bars for {}", n, sym)
            except Exception as exc:
                logger.error("Failed to collect {}: {}", sym, exc)
                results[sym] = 0

        # Build training artefacts
        self._build_feature_cache(symbols)
        self._build_episode_json(symbols)
        return results

    # ─────────────────────────────────────────────────────────
    # Bar fetching
    # ─────────────────────────────────────────────────────────

    def _fetch_bars(self, symbol: str, days: int) -> List[Dict]:
        """Fetch OHLCV daily bars from Alpaca. Falls back to synthetic."""
        if self._stock_client is None:
            return self._synthetic_bars(symbol, days)

        try:
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame

            end   = datetime.utcnow()
            start = end - timedelta(days=int(days * 1.5))  # extra buffer for holidays
            req   = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start,
                end=end,
            )
            raw  = self._stock_client.get_stock_bars(req)
            bars = raw.get(symbol, [])
            out  = []
            for b in bars:
                out.append({
                    "date":   str(b.timestamp.date()),
                    "open":   float(b.open),
                    "high":   float(b.high),
                    "low":    float(b.low),
                    "close":  float(b.close),
                    "volume": float(b.volume or 0),
                })
            return out[-days:]  # trim to requested length
        except Exception as exc:
            logger.warning("{}: Alpaca bar fetch failed ({}), using synthetic", symbol, exc)
            return self._synthetic_bars(symbol, days)

    def _synthetic_bars(self, symbol: str, days: int) -> List[Dict]:
        """GBM synthetic bars — used when API unavailable or for CI tests."""
        rng    = np.random.default_rng(abs(hash(symbol)) % (2**31))
        prices = {
            "SPY": 480.0, "QQQ": 420.0, "AAPL": 190.0,
            "MSFT": 410.0, "NVDA": 120.0, "AMD": 165.0, "AMZN": 195.0,
        }
        S0    = prices.get(symbol, 200.0)
        mu    = 0.0004     # daily drift
        sigma = 0.015      # daily vol

        bars = []
        S    = S0
        base = datetime(2024, 1, 2)
        for i in range(days):
            ret  = rng.normal(mu, sigma)
            S   *= np.exp(ret)
            vol  = abs(rng.normal(20e6, 5e6))
            bars.append({
                "date":   str((base + timedelta(days=i)).date()),
                "open":   round(S * (1 + rng.uniform(-0.002, 0.002)), 2),
                "high":   round(S * (1 + abs(rng.uniform(0, 0.01))), 2),
                "low":    round(S * (1 - abs(rng.uniform(0, 0.01))), 2),
                "close":  round(S, 2),
                "volume": round(vol, 0),
            })
        return bars

    # ─────────────────────────────────────────────────────────
    # Persistence
    # ─────────────────────────────────────────────────────────

    def _save_bars(self, symbol: str, bars: List[Dict]) -> int:
        """Save bars as JSON (Parquet if pandas available)."""
        if not bars:
            return 0
        path = CACHE_DIR / f"bars_{symbol}.json"
        path.write_text(json.dumps(bars, indent=2))

        # Try Parquet (faster for large datasets)
        try:
            import pandas as pd
            df = pd.DataFrame(bars)
            df.to_parquet(CACHE_DIR / f"bars_{symbol}.parquet", index=False)
        except ImportError:
            pass

        return len(bars)

    def load_bars(self, symbol: str) -> List[Dict]:
        """Load cached bars for a symbol."""
        parquet = CACHE_DIR / f"bars_{symbol}.parquet"
        json_f  = CACHE_DIR / f"bars_{symbol}.json"

        try:
            import pandas as pd
            if parquet.exists():
                return pd.read_parquet(parquet).to_dict("records")
        except ImportError:
            pass

        if json_f.exists():
            return json.loads(json_f.read_text())

        logger.warning("No cached bars for {} — fetching now", symbol)
        bars = self._fetch_bars(symbol, 504)
        self._save_bars(symbol, bars)
        return bars

    # ─────────────────────────────────────────────────────────
    # Feature cache (for AI training)
    # ─────────────────────────────────────────────────────────

    def _build_feature_cache(self, symbols: List[str]) -> None:
        """Pre-compute feature sequences for each symbol and save."""
        from ai.features.feature_matrix import build_sequences, bars_from_alpaca

        all_seqs = []
        for sym in symbols:
            bars = self.load_bars(sym)
            if len(bars) < 22:
                logger.warning("Skipping {}: too few bars ({})", sym, len(bars))
                continue
            try:
                std_bars = bars_from_alpaca(bars)
                seqs     = build_sequences(std_bars, lookback=20)  # (N, 20, 13)
                all_seqs.extend(seqs.tolist())
                logger.info("{}: {} sequences built", sym, len(seqs))
            except Exception as exc:
                logger.error("Feature build failed for {}: {}", sym, exc)

        # Save as flat JSON list for easy loading
        feat_path = CACHE_DIR / "all_sequences.json"
        feat_path.write_text(json.dumps(all_seqs))
        logger.info("Feature cache: {} total sequences → {}", len(all_seqs), feat_path)

    def load_sequences(self) -> List[List]:
        """Load pre-built feature sequences for AI training."""
        path = CACHE_DIR / "all_sequences.json"
        if not path.exists():
            logger.warning("Feature cache missing — run DataCollector.collect_all() first")
            return []
        return json.loads(path.read_text())

    # ─────────────────────────────────────────────────────────
    # Episode JSON (for OptionsPortfolioEnv)
    # ─────────────────────────────────────────────────────────

    def _build_episode_json(self, symbols: List[str]) -> None:
        """
        Build historical_features.json used by OptionsPortfolioEnv.
        Each episode is a list of per-day dicts keyed by symbol.
        """
        from ai.features.feature_matrix import FeatureMatrix, bars_from_alpaca

        # Load bars per symbol
        sym_bars: Dict[str, List[Dict]] = {}
        min_len = None
        for sym in symbols:
            bars = self.load_bars(sym)
            if bars:
                sym_bars[sym] = bars_from_alpaca(bars)
                min_len = min(min_len, len(bars)) if min_len else len(bars)

        if not sym_bars or not min_len:
            return

        # Build day-by-day feature snapshots
        fms = {sym: FeatureMatrix() for sym in sym_bars}
        episodes = []
        EPISODE_LEN = 252   # 1 trading year per episode

        days_data = []
        for day_idx in range(min_len):
            day_snapshot = {}
            for sym, bars in sym_bars.items():
                if day_idx >= len(bars):
                    continue
                bar = bars[day_idx]
                fms[sym].update(bar)
                feats = fms[sym].latest().tolist()
                price = float(bar["close"])
                iv    = max(feats[6], 0.15)
                iv_rk = float(feats[7])
                day_snapshot[sym] = {
                    "features":    feats,
                    "price":       price,
                    "iv":          iv,
                    "iv_rank":     iv_rk,
                    "bid_ask":     round(price * 0.001, 3),
                    "atm_premium": round(price * iv * (30 / 365) ** 0.5 * 0.4, 2),
                }
            if len(day_snapshot) == len(sym_bars):
                days_data.append(day_snapshot)

        # Split into episodes of EPISODE_LEN days
        for start in range(0, len(days_data) - EPISODE_LEN, EPISODE_LEN // 2):
            episodes.append(days_data[start: start + EPISODE_LEN])

        out_path = CACHE_DIR / "historical_features.json"
        out_path.write_text(json.dumps(episodes))
        logger.info("Episode JSON: {} episodes × {} days → {}", len(episodes), EPISODE_LEN, out_path)


# ─────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    symbols = sys.argv[1:] or None
    logger.info("Starting data collection for: {}", symbols or "all universe symbols")
    dc = DataCollector()
    results = dc.collect_all(symbols=symbols)
    logger.info("Collection complete: {}", results)
