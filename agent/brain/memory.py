"""
agent/brain/memory.py
======================
OptionAlpha Agent — Episodic Trade Memory

Short-term memory that records every trade outcome and makes
recent history available as features to the Signal Ensemble.

Capabilities:
  1. Record completed trades with full context
  2. Query recent performance per symbol ("did NVDA trades profit?")
  3. Compute recency-weighted P&L bias per symbol
  4. Provide 4 memory features for the ensemble's feature vector:
       - recent_win_rate        — last 5 trades win%
       - recent_avg_pnl_pct    — last 5 trades avg P&L %
       - symbol_bias           — symbol-specific win rate
       - days_since_last_trade — staleness signal
  5. Persist to disk so memory survives agent restarts

Memory is stored as a deque of TradeRecord dataclasses.
Max capacity: 200 completed trades (rolling).
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Deque, Dict, List, Optional

from loguru import logger


MEMORY_CAPACITY = 200        # max completed trades in memory
PERSIST_PATH    = Path("data/logs/trade_memory.json")


@dataclass
class TradeRecord:
    """A single completed trade with full context."""
    symbol:       str
    strategy:     str             # "WHEEL_CSP" | "WHEEL_CC" | "IRON_CONDOR"
    option_symbol:str
    strike:       float
    expiry:       str             # ISO date string
    dte_at_open:  int
    premium_received: float       # total credit received ($)
    pnl:          float           # realised P&L ($)
    pnl_pct:      float           # P&L / premium_received
    opened_at:    str             # ISO date
    closed_at:    str             # ISO date
    days_held:    int
    close_reason: str             # "profit_take" | "stop_loss" | "expiry" | "dte_exit"
    iv_rank_at_open: float
    regime_at_open:  str          # "Neutral" | "Bull Trend" | "Bear Trend" | "High-IV Crush"
    ensemble_signal: float        # signal score at entry
    ensemble_conf:   float        # confidence at entry
    was_profitable:  bool = field(init=False)

    def __post_init__(self):
        self.was_profitable = self.pnl > 0.0


class TradeMemory:
    """
    Rolling episodic memory for the trading agent.
    Thread-safe (GIL-protected single writer).
    """

    def __init__(self, capacity: int = MEMORY_CAPACITY, persist_path: Path = PERSIST_PATH):
        self._capacity    = capacity
        self._path        = Path(persist_path)
        self._records:    Deque[TradeRecord] = deque(maxlen=capacity)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    # ─────────────────────────────────────────────────────────
    # Write
    # ─────────────────────────────────────────────────────────
    def record(self, trade: TradeRecord) -> None:
        """Add a completed trade to memory and persist."""
        self._records.append(trade)
        self._save()
        logger.info(
            "Memory: recorded {} on {} | P&L=${:.0f} ({:.1f}%) | reason={}",
            trade.strategy, trade.symbol, trade.pnl, trade.pnl_pct * 100, trade.close_reason,
        )

    def clear(self) -> None:
        """Clear all in-memory trade records."""
        self._records.clear()

    def record_from_position(
        self,
        symbol:         str,
        strategy:       str,
        option_symbol:  str,
        strike:         float,
        expiry:         date,
        dte_at_open:    int,
        premium_received: float,
        pnl:            float,
        opened_at:      str,
        close_reason:   str,
        iv_rank_at_open:  float = 50.0,
        regime_at_open:   str   = "Neutral",
        ensemble_signal:  float = 0.0,
        ensemble_conf:    float = 0.5,
    ) -> TradeRecord:
        """Convenience builder — creates and records a TradeRecord."""
        today    = datetime.now().date()
        opened   = date.fromisoformat(opened_at[:10]) if opened_at else today
        held     = (today - opened).days

        pnl_pct  = pnl / max(abs(premium_received), 0.01)
        trade    = TradeRecord(
            symbol            = symbol,
            strategy          = strategy,
            option_symbol     = option_symbol,
            strike            = strike,
            expiry            = str(expiry),
            dte_at_open       = dte_at_open,
            premium_received  = premium_received,
            pnl               = pnl,
            pnl_pct           = pnl_pct,
            opened_at         = opened_at,
            closed_at         = str(today),
            days_held         = held,
            close_reason      = close_reason,
            iv_rank_at_open   = iv_rank_at_open,
            regime_at_open    = regime_at_open,
            ensemble_signal   = ensemble_signal,
            ensemble_conf     = ensemble_conf,
        )
        self.record(trade)
        return trade

    # ─────────────────────────────────────────────────────────
    # Query
    # ─────────────────────────────────────────────────────────
    def recent(self, n: int = 10) -> List[TradeRecord]:
        """Return the most recent n trades."""
        return list(self._records)[-n:]

    def by_symbol(self, symbol: str, n: int = 20) -> List[TradeRecord]:
        """Return last n trades on a specific symbol."""
        return [r for r in self._records if r.symbol == symbol][-n:]

    def win_rate(self, n: int = 20) -> float:
        """Overall win rate over last n trades (0–1)."""
        recent = self.recent(n)
        if not recent:
            return 0.5   # neutral prior
        return sum(1 for r in recent if r.was_profitable) / len(recent)

    def symbol_win_rate(self, symbol: str, n: int = 10) -> float:
        trades = self.by_symbol(symbol, n)
        if not trades:
            return 0.5
        return sum(1 for t in trades if t.was_profitable) / len(trades)

    def avg_pnl_pct(self, n: int = 10) -> float:
        """Average P&L percentage over last n trades."""
        recent = self.recent(n)
        if not recent:
            return 0.0
        return sum(r.pnl_pct for r in recent) / len(recent)

    def days_since_last_trade(self, symbol: Optional[str] = None) -> int:
        """Days since last completed trade (optionally filtered by symbol)."""
        trades = self.by_symbol(symbol) if symbol else self.recent()
        if not trades:
            return 999
        last_date = date.fromisoformat(trades[-1].closed_at)
        return (datetime.now().date() - last_date).days

    def strategy_stats(self) -> Dict[str, Dict]:
        """Per-strategy summary: count, win_rate, avg_pnl_pct."""
        stats: Dict[str, Dict] = {}
        for strat in ("WHEEL_CSP", "WHEEL_CC", "IRON_CONDOR"):
            trades = [r for r in self._records if r.strategy == strat]
            if not trades:
                stats[strat] = {"count": 0, "win_rate": 0.5, "avg_pnl_pct": 0.0}
            else:
                stats[strat] = {
                    "count":       len(trades),
                    "win_rate":    sum(1 for t in trades if t.was_profitable) / len(trades),
                    "avg_pnl_pct": sum(t.pnl_pct for t in trades) / len(trades),
                    "total_pnl":   sum(t.pnl for t in trades),
                }
        return stats

    # ─────────────────────────────────────────────────────────
    # Feature extraction for Ensemble
    # ─────────────────────────────────────────────────────────
    def get_memory_features(self, symbol: str) -> List[float]:
        """
        Return 4 memory-derived features for the signal ensemble:
          [recent_win_rate, recent_avg_pnl_pct, symbol_win_rate, days_since_trade_norm]

        All values are normalised to approximately [-1, 1] or [0, 1].
        """
        rwr   = self.win_rate(n=5)                    # [0, 1]
        rpp   = self.avg_pnl_pct(n=5)                 # [-∞, +∞] — clip
        swr   = self.symbol_win_rate(symbol, n=10)    # [0, 1]
        days  = self.days_since_last_trade(symbol)
        days_n = min(days / 30.0, 1.0)               # normalise: 0=today, 1=30+ days ago

        return [
            float(rwr),
            float(max(-1.0, min(1.0, rpp))),
            float(swr),
            float(days_n),
        ]

    # ─────────────────────────────────────────────────────────
    # Persistence
    # ─────────────────────────────────────────────────────────
    def _save(self) -> None:
        data = [asdict(r) for r in self._records]
        self._path.write_text(json.dumps(data, indent=2))

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text())
            for d in data[-self._capacity:]:
                d.pop("was_profitable", None)   # re-computed in __post_init__
                self._records.append(TradeRecord(**d))
            logger.info("Memory: loaded {} trade records from disk", len(self._records))
        except Exception as exc:
            logger.warning("Memory: failed to load from disk: {}", exc)

    def summary(self) -> Dict:
        return {
            "total_trades":   len(self._records),
            "win_rate_20":    round(self.win_rate(20), 3),
            "avg_pnl_pct_10": round(self.avg_pnl_pct(10), 4),
            "strategy_stats": self.strategy_stats(),
            "recent_5":       [
                {"symbol": r.symbol, "strategy": r.strategy,
                 "pnl": round(r.pnl, 2), "reason": r.close_reason}
                for r in self.recent(5)
            ],
        }

    def __len__(self) -> int:
        return len(self._records)
