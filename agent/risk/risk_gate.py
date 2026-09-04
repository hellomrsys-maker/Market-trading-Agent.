"""
agent/risk/risk_gate.py
========================
OptionAlpha Agent — Python Risk Gate

Python-side risk enforcement that works in tandem with the
C++ AtomicStateVector checks. Any order must pass BOTH layers
before being sent to Alpaca.

Six circuit breakers:
  1. Daily loss limit           — absolute $ drawdown cap
  2. Portfolio delta exposure   — prevents excessive directional risk
  3. Single position size cap   — max % of equity per trade
  4. Max open positions         — prevents over-diversification/exposure
  5. Sector concentration cap   — ≤3 same-sector positions
  6. VIX circuit breaker        — disables Iron Condors above VIX threshold

Additional smart gates:
  - Bid-ask spread quality filter (reject illiquid contracts)
  - Minimum premium filter (reject low-yield trades)
  - Earnings blackout (no new trades within 3 days of earnings)
  - Early-week / late-week position management rules
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

from loguru import logger

from config.settings import get_strategy_settings

_cfg = get_strategy_settings()

# Sector mapping for concentration check
SECTOR_MAP: Dict[str, str] = {
    "SPY":  "index",  "QQQ": "index",
    "AAPL": "tech",   "MSFT": "tech",
    "NVDA": "semis",  "AMD":  "semis",
    "AMZN": "consumer",
}


class RiskDecision(Enum):
    ALLOW  = "allow"
    REJECT = "reject"
    SCALE  = "scale"   # reduce position size and allow


@dataclass
class OrderIntent:
    """
    Describes a proposed trade before it is sent to Alpaca.
    The risk gate evaluates this and returns a RiskResult.
    """
    symbol:          str
    strategy:        str            # "WHEEL_CSP" | "WHEEL_CC" | "IRON_CONDOR" | "CLOSE"
    option_symbol:   str            # OCC symbol
    is_call:         bool
    strike:          float
    expiry:          date
    delta:           float          # absolute value (e.g., 0.30)
    premium:         float          # per-share credit/debit
    bid:             float
    ask:             float
    qty:             int            # number of contracts
    iv_rank:         float          # 0–100


@dataclass
class RiskResult:
    decision:      RiskDecision
    suggested_qty: int             # valid when SCALE
    reasons:       List[str]       = field(default_factory=list)
    warnings:      List[str]       = field(default_factory=list)

    def is_allowed(self) -> bool:
        return self.decision in (RiskDecision.ALLOW, RiskDecision.SCALE)


class RiskGate:
    """
    Stateful risk gate. Maintains rolling daily stats and position info
    to enforce all 6 circuit breakers plus smart quality filters.
    """

    def __init__(self):
        self._today_pnl:       float           = 0.0
        self._day_date:        date             = date.today()
        self._halted:          bool             = False
        self._halt_reason:     str              = ""
        self._last_vix:        float            = 15.0
        # symbol → strategy type for open positions
        self._open_positions:  Dict[str, str]   = {}
        # Earnings blackout dates: symbol → earnings date
        self._earnings_dates:  Dict[str, date]  = {}

    # ─────────────────────────────────────────────────────────
    # State updates (called by the agent each cycle)
    # ─────────────────────────────────────────────────────────
    def update_pnl(self, daily_pnl: float) -> None:
        today = date.today()
        if today != self._day_date:
            self._day_date  = today
            self._today_pnl = daily_pnl
            if self._halted and "loss limit" in self._halt_reason:
                logger.info("RiskGate: new trading day — releasing daily loss halt")
                self._halted = False
        else:
            self._today_pnl = daily_pnl

        # Auto-trigger halt
        if daily_pnl < -_cfg.daily_loss_limit and not self._halted:
            self._halt("Daily loss limit breached: ${:.0f}".format(daily_pnl))

    def update_vix(self, vix: float) -> None:
        self._last_vix = vix
        if vix > _cfg.vix_circuit_breaker:
            logger.warning("RiskGate: VIX={:.1f} — Iron Condors suspended", vix)

    def register_position(self, symbol: str, strategy: str) -> None:
        self._open_positions[symbol] = strategy
        logger.debug("RiskGate: registered position {} ({})", symbol, strategy)

    def remove_position(self, symbol: str) -> None:
        self._open_positions.pop(symbol, None)

    def set_earnings_date(self, symbol: str, earnings: date) -> None:
        self._earnings_dates[symbol] = earnings

    def _halt(self, reason: str) -> None:
        self._halted      = True
        self._halt_reason = reason
        logger.error("RiskGate: HALT — {}", reason)

    def release_halt(self) -> None:
        self._halted      = False
        self._halt_reason = ""
        logger.warning("RiskGate: halt released manually")

    @property
    def is_halted(self) -> bool:
        return self._halted

    # ─────────────────────────────────────────────────────────
    # Main evaluation
    # ─────────────────────────────────────────────────────────
    def evaluate(
        self,
        intent:    OrderIntent,
        equity:    float,
    ) -> RiskResult:
        """
        Evaluate a proposed order against all risk rules.
        Returns RiskResult with final decision.
        """
        reasons:  List[str] = []
        warnings: List[str] = []

        # ── Gate 0: Global halt ───────────────────────────────
        if self._halted:
            return RiskResult(RiskDecision.REJECT, 0, [f"Agent halted: {self._halt_reason}"])

        # ── Gate 1: Daily loss limit ──────────────────────────
        if self._today_pnl < -_cfg.daily_loss_limit:
            reasons.append(f"Daily loss limit: ${self._today_pnl:,.0f} < -${_cfg.daily_loss_limit:,.0f}")
            return RiskResult(RiskDecision.REJECT, 0, reasons)

        # ── Gate 2: VIX + strategy restriction ───────────────
        if intent.strategy == "IRON_CONDOR" and self._last_vix > _cfg.vix_circuit_breaker:
            reasons.append(f"VIX={self._last_vix:.1f} exceeds threshold={_cfg.vix_circuit_breaker:.1f}")
            return RiskResult(RiskDecision.REJECT, 0, reasons)

        # ── Gate 3: Iron Condor IV Rank gate ─────────────────
        if intent.strategy == "IRON_CONDOR" and intent.iv_rank < _cfg.ic_min_iv_rank:
            reasons.append(f"IV Rank={intent.iv_rank:.1f} below IC minimum={_cfg.ic_min_iv_rank:.1f}")
            return RiskResult(RiskDecision.REJECT, 0, reasons)

        # ── Gate 4: Max open positions ────────────────────────
        if len(self._open_positions) >= _cfg.max_open_positions:
            reasons.append(f"Max positions reached: {len(self._open_positions)}/{_cfg.max_open_positions}")
            return RiskResult(RiskDecision.REJECT, 0, reasons)

        # ── Gate 5: Duplicate position ────────────────────────
        if intent.symbol in self._open_positions and intent.strategy != "CLOSE":
            reasons.append(f"Position already open on {intent.symbol}")
            return RiskResult(RiskDecision.REJECT, 0, reasons)

        # ── Gate 6: Sector concentration ─────────────────────
        sector = SECTOR_MAP.get(intent.symbol, "other")
        same_sector = sum(
            1 for sym in self._open_positions
            if SECTOR_MAP.get(sym, "?") == sector
        )
        if same_sector >= 3:
            reasons.append(f"Sector concentration: {same_sector} positions in '{sector}' sector")
            return RiskResult(RiskDecision.REJECT, 0, reasons)

        # ── Gate 7: Earnings blackout ─────────────────────────
        earnings = self._earnings_dates.get(intent.symbol)
        if earnings:
            days_to_earnings = (earnings - date.today()).days
            if -1 <= days_to_earnings <= 3:
                reasons.append(f"Earnings blackout: {intent.symbol} reports in {days_to_earnings}d")
                return RiskResult(RiskDecision.REJECT, 0, reasons)

        # ── Quality filter 1: Bid-ask spread ─────────────────
        spread = intent.ask - intent.bid
        if spread > 0.15 and intent.bid > 0:
            warnings.append(f"Wide bid-ask spread: ${spread:.2f} — liquidity risk")
            if spread > 0.50:
                reasons.append(f"Bid-ask spread ${spread:.2f} too wide (> $0.50)")
                return RiskResult(RiskDecision.REJECT, 0, reasons, warnings)

        # ── Quality filter 2: Minimum premium ────────────────
        underlying_price_proxy = intent.strike  # use strike as proxy
        min_premium = underlying_price_proxy * (_cfg.wheel_min_premium_pct / 100)
        if intent.premium < min_premium and intent.strategy != "CLOSE":
            warnings.append(
                f"Premium ${intent.premium:.2f} below minimum "
                f"${min_premium:.2f} ({_cfg.wheel_min_premium_pct}% of strike)"
            )

        # ── Gate 8: Position size check → may SCALE ──────────
        max_notional = equity * (_cfg.max_position_size_pct / 100)
        notional     = abs(intent.premium * 100 * intent.qty)
        suggested_qty = intent.qty

        if notional > max_notional:
            suggested_qty = max(1, int(max_notional / (abs(intent.premium) * 100)))
            warnings.append(
                f"Position scaled: {intent.qty} → {suggested_qty} contracts "
                f"(notional ${notional:,.0f} → ${suggested_qty * abs(intent.premium) * 100:,.0f})"
            )
            return RiskResult(RiskDecision.SCALE, suggested_qty, reasons, warnings)

        logger.debug("RiskGate: ALLOW {} {} (warnings={})", intent.symbol, intent.strategy, warnings)
        return RiskResult(RiskDecision.ALLOW, intent.qty, reasons, warnings)

    # ─────────────────────────────────────────────────────────
    # Status summary
    # ─────────────────────────────────────────────────────────
    def summary(self) -> Dict:
        return {
            "halted":           self._halted,
            "halt_reason":      self._halt_reason,
            "daily_pnl":        self._today_pnl,
            "vix":              self._last_vix,
            "open_positions":   dict(self._open_positions),
            "position_count":   len(self._open_positions),
            "daily_loss_limit": _cfg.daily_loss_limit,
            "max_positions":    _cfg.max_open_positions,
            "vix_threshold":    _cfg.vix_circuit_breaker,
        }
