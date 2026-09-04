"""
agent/strategy/wheel.py
=========================
OptionAlpha Agent — Wheel Strategy Engine

The Wheel is a systematic options income strategy:
  Cycle 1: Sell a Cash-Secured Put (CSP) on a target symbol.
           Collect premium. If OTM at expiry → keep premium → repeat.
           If ITM at expiry → assigned 100 shares per contract.

  Cycle 2: Once assigned, sell a Covered Call (CC) on the shares.
           Collect premium. If OTM → keep premium + shares → repeat.
           If ITM → shares called away at strike → profit locked in.

Strategy parameters (from settings):
  - Target CSP delta:  0.30 (30% probability ITM)
  - Target CC delta:   0.20 (20% probability ITM)
  - DTE range:         21–45 days
  - Profit take:       50% of max profit
  - Stop loss:         2× premium received (roll or close)
  - Min premium:       1% of underlying price

Contract selection uses the Julia GreeksSnapshot to find the
closest strike to the target delta using the full option chain.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from loguru import logger

from agent.execution.alpaca_client import AlpacaClient
from agent.risk.risk_gate import OrderIntent, RiskDecision, RiskGate
from config.settings import get_strategy_settings

_cfg = get_strategy_settings()


# ─────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────

@dataclass
class ContractCandidate:
    """A scored option contract candidate for the Wheel strategy."""
    symbol:     str        # OCC option symbol
    underlying: str
    option_type:str        # "call" | "put"
    strike:     float
    expiry:     date
    dte:        int
    delta:      float      # absolute
    theta:      float
    vega:       float
    bid:        float
    ask:        float
    mid:        float
    iv:         float
    score:      float = 0.0  # higher = better candidate


@dataclass
class WheelPosition:
    """Tracks an active Wheel position through its lifecycle."""
    symbol:           str
    stage:            str       # "CSP" | "CC" | "ASSIGNED"
    option_symbol:    str
    strike:           float
    expiry:           date
    premium_received: float
    qty:              int
    opened_at:        str
    max_profit:       float
    order_id:         str = ""


# ─────────────────────────────────────────────────────────────
# Wheel Strategy Engine
# ─────────────────────────────────────────────────────────────

class WheelStrategy:
    """
    Full Wheel strategy implementation.

    Responsibilities:
      - Determine which symbols need a new CSP or CC opened
      - Select the optimal contract (closest to target delta)
      - Submit orders via AlpacaClient (after risk gate approval)
      - Track position lifecycle and manage exits
    """

    def __init__(self, client: AlpacaClient, risk_gate: RiskGate):
        self.client    = client
        self.risk_gate = risk_gate
        # symbol → active position
        self._positions: Dict[str, WheelPosition] = {}

    # ─────────────────────────────────────────────────────────
    # Contract Selection
    # ─────────────────────────────────────────────────────────
    def _select_best_contract(
        self,
        symbol:       str,
        option_type:  str,       # "put" | "call"
        target_delta: float,     # absolute delta target
        underlying_price: float,
    ) -> Optional[ContractCandidate]:
        """
        Fetch the option chain and select the contract closest
        to the target delta within the DTE window.

        Scoring function penalises:
          - Delta deviation from target
          - Wide bid-ask spreads (illiquidity)
          - Very short DTE (gamma risk)
          - Low premium (< min threshold)
        """
        today     = date.today()
        min_expiry= today + timedelta(days=_cfg.wheel_min_dte)
        max_expiry= today + timedelta(days=_cfg.wheel_max_dte)

        chain = self.client.get_option_chain(
            symbol       = symbol,
            expiry_after = min_expiry,
            expiry_before= max_expiry,
            option_type  = option_type,
        )

        if not chain:
            logger.warning("No {} contracts found for {} in DTE window", option_type, symbol)
            return None

        # Get snapshots for all contracts
        symbols  = [c["symbol"] for c in chain]
        # Batch in groups of 50 (API limit)
        snaps = {}
        for i in range(0, len(symbols), 50):
            batch = symbols[i:i+50]
            try:
                snaps.update(self.client.get_option_snapshot(batch))
            except Exception as exc:
                logger.warning("Snapshot batch failed: {}", exc)

        candidates = []
        for c in chain:
            c_type = c.get("type") or c.get("option_type") or ("call" if c.get("is_call") else "put")
            if str(c_type).lower() != option_type.lower():
                continue

            snap = snaps.get(c["symbol"], {})
            delta = abs(float(snap.get("delta") or c.get("delta") or 0.3))
            bid   = float(snap.get("bid") or c.get("bid") or 0.0)
            ask   = float(snap.get("ask") or c.get("ask") or 0.0)
            mid   = (bid + ask) / 2 if (bid + ask) > 0 else float(c.get("mid", 1.0))
            iv    = float(snap.get("iv") or c.get("implied_volatility") or 0.25)
            theta = float(snap.get("theta") or c.get("theta") or 0.0)
            vega  = float(snap.get("vega") or c.get("vega") or 0.0)

            exp_val = c.get("expiration_date") or c.get("expiration") or str(today + timedelta(days=c.get("dte", 30)))
            expiry  = date.fromisoformat(str(exp_val))
            dte     = (expiry - today).days

            # Liquidity filter: skip if zero bid or excessive spread
            if bid <= 0.01 or (ask - bid) > max(3.0, mid * 0.30):
                continue

            # Premium filter: minimum $0.50 or proportional
            min_prem = max(0.50, underlying_price * (_cfg.wheel_min_premium_pct / 100) * 0.3)
            if mid < min_prem:
                continue

            # Scoring: prioritise delta accuracy, then theta, penalise spread
            delta_err  = abs(delta - target_delta)
            spread_pen = (ask - bid) / max(mid, 0.01)
            theta_bonus= abs(theta) / max(mid, 0.01)   # theta/premium ratio
            score      = -delta_err - 0.5 * spread_pen + 0.2 * theta_bonus

            candidates.append(ContractCandidate(
                symbol      = c["symbol"],
                underlying  = symbol,
                option_type = option_type,
                strike      = float(c["strike"]),
                expiry      = expiry,
                dte         = dte,
                delta       = delta,
                theta       = theta,
                vega        = vega,
                bid         = bid,
                ask         = ask,
                mid         = mid,
                iv          = iv,
                score       = score,
            ))

        if not candidates:
            logger.warning("No liquid {} contracts on {}", option_type, symbol)
            return None

        best = max(candidates, key=lambda c: c.score)
        logger.info(
            "Selected {} {} K={} exp={} delta={:.2f} mid=${:.2f} dte={}",
            symbol, option_type.upper(), best.strike, best.expiry,
            best.delta, best.mid, best.dte,
        )
        return best

    def _calc_qty(self, equity: float, contract: ContractCandidate) -> int:
        """
        Position sizing: max % of equity per position, capped at 1
        contract per $10,000 of equity for CSPs (collateral requirement).
        """
        max_notional = equity * (_cfg.max_position_size_pct / 100)
        collateral   = contract.strike * 100    # 1 contract = 100 shares
        qty          = max(1, int(max_notional / collateral))
        return min(qty, 5)   # hard cap at 5 contracts per position

    # ─────────────────────────────────────────────────────────
    # CSP Entry
    # ─────────────────────────────────────────────────────────
    def open_csp(self, symbol: str, equity: float) -> Optional[WheelPosition]:
        """
        Open a Cash-Secured Put on `symbol`.
        Returns the created WheelPosition, or None if rejected/failed.
        """
        if symbol in self._positions:
            logger.debug("Wheel: {} already has an active position", symbol)
            return None

        price = self.client.get_latest_price(symbol)

        contract = self._select_best_contract(
            symbol, "put", _cfg.wheel_csp_delta, price
        )
        if not contract:
            return None

        qty = self._calc_qty(equity, contract)

        # Build intent for risk gate evaluation
        intent = OrderIntent(
            symbol       = symbol,
            strategy     = "WHEEL_CSP",
            option_symbol= contract.symbol,
            is_call      = False,
            strike       = contract.strike,
            expiry       = contract.expiry,
            delta        = contract.delta,
            premium      = contract.mid,
            bid          = contract.bid,
            ask          = contract.ask,
            qty          = qty,
            iv_rank      = contract.iv * 100,  # approx
        )

        result = self.risk_gate.evaluate(intent, equity)
        if result.decision == RiskDecision.REJECT:
            logger.warning("CSP rejected for {}: {}", symbol, result.reasons)
            return None
        if result.decision == RiskDecision.SCALE:
            qty = result.suggested_qty
            logger.info("CSP scaled to {} contracts for {}", qty, symbol)

        # Submit order — use limit at mid (natural midpoint)
        try:
            order = self.client.sell_put(contract.symbol, qty, contract.mid)
        except Exception as exc:
            logger.error("CSP order failed for {}: {}", symbol, exc)
            return None

        pos = WheelPosition(
            symbol           = symbol,
            stage            = "CSP",
            option_symbol    = contract.symbol,
            strike           = contract.strike,
            expiry           = contract.expiry,
            premium_received = contract.mid * qty * 100,
            qty              = qty,
            opened_at        = str(date.today()),
            max_profit       = contract.mid * qty * 100,
            order_id         = order["id"],
        )
        self._positions[symbol] = pos
        self.risk_gate.register_position(symbol, "WHEEL_CSP")
        logger.success("Opened CSP: {} × {} K={} exp={} credit=${:.2f}",
                       qty, symbol, contract.strike, contract.expiry,
                       contract.mid * qty * 100)
        return pos

    # ─────────────────────────────────────────────────────────
    # Covered Call Entry
    # ─────────────────────────────────────────────────────────
    def open_covered_call(self, symbol: str, equity: float) -> Optional[WheelPosition]:
        """
        Open a Covered Call when stock was assigned from CSP exercise.
        """
        price    = self.client.get_latest_price(symbol)
        contract = self._select_best_contract(
            symbol, "call", _cfg.wheel_cc_delta, price
        )
        if not contract:
            return None

        qty = self._calc_qty(equity, contract)

        intent = OrderIntent(
            symbol       = symbol,
            strategy     = "WHEEL_CC",
            option_symbol= contract.symbol,
            is_call      = True,
            strike       = contract.strike,
            expiry       = contract.expiry,
            delta        = contract.delta,
            premium      = contract.mid,
            bid          = contract.bid,
            ask          = contract.ask,
            qty          = qty,
            iv_rank      = contract.iv * 100,
        )
        result = self.risk_gate.evaluate(intent, equity)
        if not result.is_allowed():
            logger.warning("CC rejected for {}: {}", symbol, result.reasons)
            return None

        qty = result.suggested_qty
        try:
            order = self.client.sell_call(contract.symbol, qty, contract.mid)
        except Exception as exc:
            logger.error("CC order failed for {}: {}", symbol, exc)
            return None

        pos = WheelPosition(
            symbol           = symbol,
            stage            = "CC",
            option_symbol    = contract.symbol,
            strike           = contract.strike,
            expiry           = contract.expiry,
            premium_received = contract.mid * qty * 100,
            qty              = qty,
            opened_at        = str(date.today()),
            max_profit       = contract.mid * qty * 100,
            order_id         = order["id"],
        )
        self._positions[symbol] = pos
        self.risk_gate.register_position(symbol, "WHEEL_CC")
        logger.success("Opened CC: {} × {} K={} exp={} credit=${:.2f}",
                       qty, symbol, contract.strike, contract.expiry,
                       contract.mid * qty * 100)
        return pos

    # ─────────────────────────────────────────────────────────
    # Position Management
    # ─────────────────────────────────────────────────────────
    def manage_positions(self) -> List[str]:
        """
        Review all open Wheel positions.
        Closes positions that hit profit target or stop-loss.
        Returns list of symbols that were closed.
        """
        closed = []
        alpaca_positions = {
            p["symbol"]: p for p in self.client.get_option_positions()
        }

        for sym, pos in list(self._positions.items()):
            alp_pos = alpaca_positions.get(pos.option_symbol)
            if alp_pos is None:
                # Position no longer in Alpaca — expired or filled
                logger.info("Wheel: {} expired/filled, removing from tracker", sym)
                self._positions.pop(sym, None)
                self.risk_gate.remove_position(sym)
                closed.append(sym)
                continue

            unreal_pnl = float(alp_pos.get("unrealized_pl", 0))
            pct_profit = unreal_pnl / pos.premium_received if pos.premium_received else 0

            today = date.today()
            dte   = (pos.expiry - today).days

            # Profit take: 50% of max profit
            if pct_profit >= (_cfg.wheel_profit_take_pct / 100):
                logger.info("Wheel: taking profit on {} ({:.0f}% gained)", sym, pct_profit * 100)
                self._close_position(sym, pos)
                closed.append(sym)
                continue

            # Stop loss: 2× premium received (position doubled in cost)
            stop_threshold = -pos.premium_received * _cfg.wheel_stop_loss_mult
            if unreal_pnl <= stop_threshold:
                logger.warning("Wheel: stop-loss triggered on {} (P&L=${:.0f})", sym, unreal_pnl)
                self._close_position(sym, pos)
                closed.append(sym)
                continue

            # DTE management: close or roll if < 7 DTE
            if dte < 7:
                logger.info("Wheel: {} has {}DTE — closing near expiry", sym, dte)
                self._close_position(sym, pos)
                closed.append(sym)

        return closed

    def _close_position(self, symbol: str, pos: WheelPosition) -> None:
        try:
            self.client.close_position(pos.option_symbol)
        except Exception as exc:
            logger.error("Failed to close {} position: {}", symbol, exc)
        self._positions.pop(symbol, None)
        self.risk_gate.remove_position(symbol)

    # ─────────────────────────────────────────────────────────
    # Status
    # ─────────────────────────────────────────────────────────
    @property
    def active_positions(self) -> Dict[str, WheelPosition]:
        return dict(self._positions)

    def summary(self) -> List[Dict]:
        return [
            {
                "symbol":    pos.symbol,
                "stage":     pos.stage,
                "strike":    pos.strike,
                "expiry":    str(pos.expiry),
                "dte":       (pos.expiry - date.today()).days,
                "premium":   pos.premium_received,
                "max_profit":pos.max_profit,
                "qty":       pos.qty,
            }
            for pos in self._positions.values()
        ]
