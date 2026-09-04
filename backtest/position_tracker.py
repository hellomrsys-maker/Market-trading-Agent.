"""
backtest/position_tracker.py
=============================
OptionAlpha Agent — Position & Portfolio Tracker for Backtesting

Simulates order execution, position lifecycle (CSP -> Assignment -> CC -> Call Away, or Iron Condor),
daily mark-to-market, profit-taking, stop-losses, and historical trade logs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional
from loguru import logger

from backtest.option_chain_sim import bsm_price


@dataclass
class SimulatedTrade:
    trade_id: str
    symbol: str
    strategy: str          # "WHEEL_CSP", "WHEEL_CC", "IRON_CONDOR"
    open_date: str
    close_date: Optional[str] = None
    expiry_date: str = ""
    dte_at_open: int = 0
    days_held: int = 0
    contracts: int = 1
    strike: float = 0.0
    entry_credit: float = 0.0     # total $ premium collected at entry
    exit_debit: float = 0.0       # total $ paid to close/expire
    realized_pnl: float = 0.0     # entry_credit - exit_debit
    return_pct: float = 0.0       # realized_pnl / abs(entry_credit or max_risk)
    close_reason: str = ""        # "PROFIT_TAKE", "STOP_LOSS", "EXPIRATION", "ASSIGNMENT", "CALL_AWAY"
    extra: Dict = field(default_factory=dict)


class PositionTracker:
    """
    Maintains simulated active positions and cash balances during a backtest run.
    """

    def __init__(self, initial_cash: float = 100_000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.csp_positions: List[Dict] = []
        self.cc_positions: List[Dict] = []
        self.ic_positions: List[Dict] = []
        self.shares_held: Dict[str, Dict] = {}  # {symbol: {"qty": int, "avg_cost": float}}
        self.closed_trades: List[SimulatedTrade] = []
        self.daily_pnl_history: List[Dict] = []
        self._next_id = 1

    def _get_id(self) -> str:
        tid = f"TRD_{self._next_id:05d}"
        self._next_id += 1
        return tid

    # ─────────────────────────────────────────────────────────────
    # Order Openers
    # ─────────────────────────────────────────────────────────────

    def open_csp(
        self,
        symbol: str,
        contract_symbol: str,
        strike: float,
        expiry: str,
        dte: int,
        premium: float,
        qty: int,
        date_str: str,
        iv: float,
    ) -> Dict:
        total_credit = premium * 100.0 * qty
        self.cash += total_credit
        pos = {
            "id": self._get_id(),
            "symbol": symbol,
            "contract_symbol": contract_symbol,
            "strike": strike,
            "expiry": expiry,
            "dte_remaining": dte,
            "initial_dte": dte,
            "initial_premium": premium,
            "current_premium": premium,
            "qty": qty,
            "open_date": date_str,
            "initial_iv": iv,
            "collateral": strike * 100.0 * qty,
        }
        self.csp_positions.append(pos)
        return pos

    def open_cc(
        self,
        symbol: str,
        contract_symbol: str,
        strike: float,
        expiry: str,
        dte: int,
        premium: float,
        qty: int,
        date_str: str,
        iv: float,
    ) -> Dict:
        total_credit = premium * 100.0 * qty
        self.cash += total_credit
        pos = {
            "id": self._get_id(),
            "symbol": symbol,
            "contract_symbol": contract_symbol,
            "strike": strike,
            "expiry": expiry,
            "dte_remaining": dte,
            "initial_dte": dte,
            "initial_premium": premium,
            "current_premium": premium,
            "qty": qty,
            "open_date": date_str,
            "initial_iv": iv,
        }
        self.cc_positions.append(pos)
        return pos

    def open_iron_condor(
        self,
        symbol: str,
        short_put: float,
        long_put: float,
        short_call: float,
        long_call: float,
        expiry: str,
        dte: int,
        net_credit: float,
        wing_width: float,
        qty: int,
        date_str: str,
        iv: float,
    ) -> Dict:
        total_credit = net_credit * 100.0 * qty
        self.cash += total_credit
        pos = {
            "id": self._get_id(),
            "symbol": symbol,
            "short_put": short_put,
            "long_put": long_put,
            "short_call": short_call,
            "long_call": long_call,
            "expiry": expiry,
            "dte_remaining": dte,
            "initial_dte": dte,
            "initial_credit": net_credit,
            "current_cost": net_credit,
            "wing_width": wing_width,
            "max_loss": (wing_width - net_credit) * 100.0 * qty,
            "qty": qty,
            "open_date": date_str,
            "initial_iv": iv,
        }
        self.ic_positions.append(pos)
        return pos

    # ─────────────────────────────────────────────────────────────
    # Daily Mark-To-Market & Exits
    # ─────────────────────────────────────────────────────────────

    def process_day(
        self,
        current_date: date,
        spot_prices: Dict[str, float],
        iv_estimates: Dict[str, float],
        profit_take_pct: float = 0.50,
        stop_loss_mult: float = 2.0,
    ) -> None:
        date_str = current_date.strftime("%Y-%m-%d")

        # ── 1. Process Cash-Secured Puts ──────────────────────────
        remaining_csp = []
        for pos in self.csp_positions:
            sym = pos["symbol"]
            spot = spot_prices.get(sym, pos["strike"])
            iv = iv_estimates.get(sym, pos["initial_iv"])
            pos["dte_remaining"] -= 1
            dte = max(0, pos["dte_remaining"])

            curr_price = bsm_price(spot, pos["strike"], dte, iv, is_call=False)
            pos["current_premium"] = curr_price

            initial_prem = pos["initial_premium"]
            qty = pos["qty"]
            days_held = pos["initial_dte"] - dte

            if curr_price <= initial_prem * (1.0 - profit_take_pct):
                exit_debit = curr_price * 100.0 * qty
                self.cash -= exit_debit
                pnl = (initial_prem - curr_price) * 100.0 * qty
                self._record_closed_trade(
                    pos, "WHEEL_CSP", date_str, days_held, exit_debit, pnl, "PROFIT_TAKE"
                )
            elif curr_price >= initial_prem * stop_loss_mult:
                exit_debit = curr_price * 100.0 * qty
                self.cash -= exit_debit
                pnl = (initial_prem - curr_price) * 100.0 * qty
                self._record_closed_trade(
                    pos, "WHEEL_CSP", date_str, days_held, exit_debit, pnl, "STOP_LOSS"
                )
            elif dte <= 0:
                if spot < pos["strike"]:
                    shares_to_buy = 100 * qty
                    cost = pos["strike"] * shares_to_buy
                    self.cash -= cost

                    if sym not in self.shares_held:
                        self.shares_held[sym] = {"qty": 0, "avg_cost": 0.0}
                    prev = self.shares_held[sym]
                    total_shares = prev["qty"] + shares_to_buy
                    prev["avg_cost"] = ((prev["qty"] * prev["avg_cost"]) + cost) / total_shares
                    prev["qty"] = total_shares

                    pnl = (initial_prem - (pos["strike"] - spot)) * 100.0 * qty
                    self._record_closed_trade(
                        pos, "WHEEL_CSP", date_str, days_held, 0.0, pnl, "ASSIGNED"
                    )
                else:
                    pnl = initial_prem * 100.0 * qty
                    self._record_closed_trade(
                        pos, "WHEEL_CSP", date_str, days_held, 0.0, pnl, "EXPIRED_WORTHLESS"
                    )
            else:
                remaining_csp.append(pos)
        self.csp_positions = remaining_csp

        # ── 2. Process Covered Calls ──────────────────────────────
        remaining_cc = []
        for pos in self.cc_positions:
            sym = pos["symbol"]
            spot = spot_prices.get(sym, pos["strike"])
            iv = iv_estimates.get(sym, pos["initial_iv"])
            pos["dte_remaining"] -= 1
            dte = max(0, pos["dte_remaining"])

            curr_price = bsm_price(spot, pos["strike"], dte, iv, is_call=True)
            pos["current_premium"] = curr_price

            initial_prem = pos["initial_premium"]
            qty = pos["qty"]
            days_held = pos["initial_dte"] - dte

            if curr_price <= initial_prem * (1.0 - profit_take_pct):
                exit_debit = curr_price * 100.0 * qty
                self.cash -= exit_debit
                pnl = (initial_prem - curr_price) * 100.0 * qty
                self._record_closed_trade(
                    pos, "WHEEL_CC", date_str, days_held, exit_debit, pnl, "PROFIT_TAKE"
                )
            elif curr_price >= initial_prem * stop_loss_mult:
                exit_debit = curr_price * 100.0 * qty
                self.cash -= exit_debit
                pnl = (initial_prem - curr_price) * 100.0 * qty
                self._record_closed_trade(
                    pos, "WHEEL_CC", date_str, days_held, exit_debit, pnl, "STOP_LOSS"
                )
            elif dte <= 0:
                if spot > pos["strike"]:
                    shares_to_sell = 100 * qty
                    revenue = pos["strike"] * shares_to_sell
                    self.cash += revenue

                    if sym in self.shares_held:
                        self.shares_held[sym]["qty"] = max(0, self.shares_held[sym]["qty"] - shares_to_sell)
                        if self.shares_held[sym]["qty"] == 0:
                            del self.shares_held[sym]

                    pnl = initial_prem * 100.0 * qty
                    self._record_closed_trade(
                        pos, "WHEEL_CC", date_str, days_held, 0.0, pnl, "CALLED_AWAY"
                    )
                else:
                    pnl = initial_prem * 100.0 * qty
                    self._record_closed_trade(
                        pos, "WHEEL_CC", date_str, days_held, 0.0, pnl, "EXPIRED_WORTHLESS"
                    )
            else:
                remaining_cc.append(pos)
        self.cc_positions = remaining_cc

        # ── 3. Process Iron Condors ───────────────────────────────
        remaining_ic = []
        for pos in self.ic_positions:
            sym = pos["symbol"]
            spot = spot_prices.get(sym, (pos["short_put"] + pos["short_call"]) / 2.0)
            iv = iv_estimates.get(sym, pos["initial_iv"])
            pos["dte_remaining"] -= 1
            dte = max(0, pos["dte_remaining"])

            p_sp = bsm_price(spot, pos["short_put"], dte, iv, is_call=False)
            p_lp = bsm_price(spot, pos["long_put"], dte, iv, is_call=False)
            p_sc = bsm_price(spot, pos["short_call"], dte, iv, is_call=True)
            p_lc = bsm_price(spot, pos["long_call"], dte, iv, is_call=True)

            current_cost = max(0.0, (p_sp - p_lp) + (p_sc - p_lc))
            pos["current_cost"] = current_cost

            initial_cred = pos["initial_credit"]
            qty = pos["qty"]
            days_held = pos["initial_dte"] - dte

            if current_cost <= initial_cred * (1.0 - profit_take_pct):
                exit_debit = current_cost * 100.0 * qty
                self.cash -= exit_debit
                pnl = (initial_cred - current_cost) * 100.0 * qty
                self._record_closed_trade(
                    pos, "IRON_CONDOR", date_str, days_held, exit_debit, pnl, "PROFIT_TAKE"
                )
            elif current_cost >= initial_cred * stop_loss_mult:
                exit_debit = current_cost * 100.0 * qty
                self.cash -= exit_debit
                pnl = (initial_cred - current_cost) * 100.0 * qty
                self._record_closed_trade(
                    pos, "IRON_CONDOR", date_str, days_held, exit_debit, pnl, "STOP_LOSS"
                )
            elif dte <= 0:
                intrinsic_loss = 0.0
                if spot < pos["short_put"]:
                    intrinsic_loss = min(pos["wing_width"], pos["short_put"] - spot)
                elif spot > pos["short_call"]:
                    intrinsic_loss = min(pos["wing_width"], spot - pos["short_call"])

                exit_debit = intrinsic_loss * 100.0 * qty
                self.cash -= exit_debit
                pnl = (initial_cred - intrinsic_loss) * 100.0 * qty
                reason = "EXPIRED_FULL_PROFIT" if intrinsic_loss == 0 else "EXPIRED_WITH_LOSS"
                self._record_closed_trade(
                    pos, "IRON_CONDOR", date_str, days_held, exit_debit, pnl, reason
                )
            else:
                remaining_ic.append(pos)
        self.ic_positions = remaining_ic

        portfolio_val = self.get_portfolio_value(spot_prices)
        self.daily_pnl_history.append({
            "date": date_str,
            "portfolio_value": round(portfolio_val, 2),
            "cash": round(self.cash, 2),
            "open_positions": len(self.csp_positions) + len(self.cc_positions) + len(self.ic_positions),
            "shares_value": sum(
                h["qty"] * spot_prices.get(s, h["avg_cost"])
                for s, h in self.shares_held.items()
            ),
        })

    def _record_closed_trade(
        self,
        pos: Dict,
        strategy: str,
        close_date: str,
        days_held: int,
        exit_debit: float,
        pnl: float,
        reason: str
    ) -> None:
        initial_prem = pos.get("initial_premium", pos.get("initial_credit", 0.0))
        qty = pos["qty"]
        entry_cred = initial_prem * 100.0 * qty
        trade = SimulatedTrade(
            trade_id=pos["id"],
            symbol=pos["symbol"],
            strategy=strategy,
            open_date=pos["open_date"],
            close_date=close_date,
            expiry_date=pos.get("expiry", ""),
            dte_at_open=pos["initial_dte"],
            days_held=days_held,
            contracts=qty,
            strike=pos.get("strike", pos.get("short_put", 0.0)),
            entry_credit=entry_cred,
            exit_debit=exit_debit,
            realized_pnl=pnl,
            return_pct=pnl / max(0.01, entry_cred),
            close_reason=reason,
        )
        self.closed_trades.append(trade)

    def get_portfolio_value(self, current_spots: Dict[str, float]) -> float:
        val = self.cash
        for sym, h in self.shares_held.items():
            spot = current_spots.get(sym, h["avg_cost"])
            val += h["qty"] * spot

        for pos in self.csp_positions:
            val -= pos["current_premium"] * 100.0 * pos["qty"]

        for pos in self.cc_positions:
            val -= pos["current_premium"] * 100.0 * pos["qty"]

        for pos in self.ic_positions:
            val -= pos["current_cost"] * 100.0 * pos["qty"]

        return val
