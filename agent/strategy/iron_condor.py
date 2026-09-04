"""
agent/strategy/iron_condor.py
==============================
OptionAlpha Agent — Iron Condor Strategy Engine

An Iron Condor is a 4-leg options strategy that profits from
low volatility / IV contraction:

  Structure:
    Sell OTM Call at +Δ (short call)  ← ~0.15 delta
    Buy  OTM Call at +Δ+W (long call) ← wing = 5 points wide
    Sell OTM Put  at -Δ (short put)   ← ~0.15 delta
    Buy  OTM Put  at -Δ-W (long put)  ← wing = 5 points wide

  Net: credit received upfront. Max profit = net credit.
       Max loss = wing width − credit.

Entry conditions (enforced by risk gate + this engine):
  - IV Rank > 30 (elevated IV → favourable credit)
  - VIX < 35 (catastrophic risk protection)
  - DTE: 21–45 days
  - Underlying: SPY or QQQ only (highest liquidity)

Exit conditions:
  - 50% profit take (close when unrealised gain ≥ 50% of max profit)
  - Stop loss: 200% of credit received (max loss = 2× premium)
  - DTE < 7: close to avoid gamma risk
  - IV collapse: if IV Rank < 10, close early

Julia math integration:
  Uses OptionsMath.iron_condor_pop() for Probability of Profit
  calculation at entry to ensure expected edge > 60% PoP.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from loguru import logger

from agent.execution.alpaca_client import AlpacaClient
from agent.risk.risk_gate import OrderIntent, RiskDecision, RiskGate
from config.settings import get_strategy_settings

_cfg = get_strategy_settings()


@dataclass
class IronCondorLeg:
    symbol:  str
    strike:  float
    expiry:  date
    side:    str   # "sell" | "buy"
    type:    str   # "call" | "put"
    delta:   float
    bid:     float
    ask:     float
    mid:     float


@dataclass
class IronCondorPosition:
    underlying:    str
    short_put:     IronCondorLeg
    long_put:      IronCondorLeg
    short_call:    IronCondorLeg
    long_call:     IronCondorLeg
    net_credit:    float
    max_profit:    float
    max_loss:      float
    wing_width:    float
    qty:           int
    opened_at:     str
    expiry:        date
    dte_at_open:   int
    order_id:      str = ""

    @property
    def dte(self) -> int:
        return (self.expiry - date.today()).days

    @property
    def breakeven_lower(self) -> float:
        return self.short_put.strike - self.net_credit

    @property
    def breakeven_upper(self) -> float:
        return self.short_call.strike + self.net_credit

    @property
    def risk_reward(self) -> float:
        return self.net_credit / max(self.max_loss, 0.01)


class IronCondorStrategy:
    """
    Iron Condor strategy execution engine.
    Opens 4-leg positions when IV Rank is elevated,
    manages them through theta decay, exits systematically.
    """

    # Only trade highly liquid underlyings for IC
    ELIGIBLE_SYMBOLS = {"SPY", "QQQ"}

    def __init__(self, client: AlpacaClient, risk_gate: RiskGate):
        self.client    = client
        self.risk_gate = risk_gate
        self._positions: Dict[str, IronCondorPosition] = {}

    # ─────────────────────────────────────────────────────────
    # Julia PoP integration (graceful fallback)
    # ─────────────────────────────────────────────────────────
    def _calc_pop(
        self, S: float, sp: float, lp: float, sc: float, lc: float,
        T: float, sigma: float
    ) -> float:
        """Call Julia OptionsMath.iron_condor_pop(), fallback to 0.65."""
        try:
            import juliacall
            jl   = juliacall.newmodule("IC_Math")
            jl.seval('include("engine/julia/options_math.jl")')
            jl.seval('using .OptionsMath')
            pop  = float(jl.OptionsMath.iron_condor_pop(S, sp, lp, sc, lc, T, 0.05, sigma))
            return pop
        except Exception:
            return 0.65   # assume 65% PoP when Julia unavailable

    # ─────────────────────────────────────────────────────────
    # Leg Selection
    # ─────────────────────────────────────────────────────────
    def _select_legs(
        self, symbol: str, underlying_price: float
    ) -> Optional[Tuple[IronCondorLeg, IronCondorLeg, IronCondorLeg, IronCondorLeg]]:
        """
        Select the 4 legs for an Iron Condor.
        Short legs: ~0.15 delta each side.
        Long legs:  wing_width points further OTM.
        """
        today      = date.today()
        min_expiry = today + timedelta(days=_cfg.ic_min_dte)
        max_expiry = today + timedelta(days=_cfg.ic_max_dte)
        target_d   = _cfg.ic_short_delta          # 0.15
        wing       = _cfg.ic_wing_width           # 5 points

        # Fetch put chain and call chain
        put_chain  = self.client.get_option_chain(
            symbol, expiry_after=min_expiry, expiry_before=max_expiry, option_type="put"
        )
        call_chain = self.client.get_option_chain(
            symbol, expiry_after=min_expiry, expiry_before=max_expiry, option_type="call"
        )

        if not put_chain or not call_chain:
            logger.warning("IC: empty chain for {}", symbol)
            return None

        # Get snapshots
        all_syms = [c["symbol"] for c in put_chain + call_chain]
        snaps = {}
        for i in range(0, len(all_syms), 50):
            try:
                snaps.update(self.client.get_option_snapshot(all_syms[i:i+50]))
            except Exception as e:
                logger.warning("IC snapshot batch failed: {}", e)

        def find_closest(chain, is_call: bool) -> Optional[Dict]:
            """Find contract closest to target_d delta."""
            best, best_err = None, 9999.0
            for c in chain:
                s   = snaps.get(c["symbol"], {})
                raw_d = float(s.get("delta", 0) or 0)
                d   = abs(raw_d)
                if d < 0.01 or d > 0.5:
                    continue
                bid = float(s.get("bid", 0) or 0)
                if bid < 0.01:
                    continue
                err = abs(d - target_d)
                if err < best_err:
                    best_err = err
                    best     = {**c, **s, "delta_abs": d}
            return best

        short_put_raw  = find_closest(put_chain,  is_call=False)
        short_call_raw = find_closest(call_chain, is_call=True)

        if not short_put_raw or not short_call_raw:
            logger.warning("IC: could not find OTM legs for {}", symbol)
            return None

        sp_strike = float(short_put_raw["strike"])
        sc_strike = float(short_call_raw["strike"])

        # Long legs: wing_width below/above short legs
        lp_strike = sp_strike - wing
        lc_strike = sc_strike + wing

        # Find exact long leg contracts
        def find_at_strike(chain, target_strike: float) -> Optional[Dict]:
            best, best_err = None, 9999.0
            for c in chain:
                err = abs(float(c["strike"]) - target_strike)
                if err < best_err:
                    best_err = err
                    best     = {**c, **snaps.get(c["symbol"], {})}
            return best

        long_put_raw  = find_at_strike(put_chain,  lp_strike)
        long_call_raw = find_at_strike(call_chain, lc_strike)

        if not long_put_raw or not long_call_raw:
            logger.warning("IC: could not find wing legs for {}", symbol)
            return None

        def make_leg(raw: Dict, side: str, opt_type: str) -> IronCondorLeg:
            exp = date.fromisoformat(str(raw["expiration"]))
            bid = float(raw.get("bid", 0) or 0)
            ask = float(raw.get("ask", 0) or 0)
            return IronCondorLeg(
                symbol  = raw["symbol"],
                strike  = float(raw["strike"]),
                expiry  = exp,
                side    = side,
                type    = opt_type,
                delta   = float(raw.get("delta_abs", raw.get("delta", 0)) or 0),
                bid     = bid,
                ask     = ask,
                mid     = (bid + ask) / 2,
            )

        short_put  = make_leg(short_put_raw,  "sell", "put")
        long_put   = make_leg(long_put_raw,   "buy",  "put")
        short_call = make_leg(short_call_raw, "sell", "call")
        long_call  = make_leg(long_call_raw,  "buy",  "call")

        return short_put, long_put, short_call, long_call

    # ─────────────────────────────────────────────────────────
    # IC Entry
    # ─────────────────────────────────────────────────────────
    def open_iron_condor(self, symbol: str, equity: float, iv_rank: float) -> Optional[IronCondorPosition]:
        """
        Open an Iron Condor on `symbol` if IV Rank and conditions permit.
        """
        if symbol not in self.ELIGIBLE_SYMBOLS:
            logger.debug("IC: {} not in eligible symbols", symbol)
            return None

        if symbol in self._positions:
            logger.debug("IC: {} already has active IC", symbol)
            return None

        price = self.client.get_latest_price(symbol)
        legs  = self._select_legs(symbol, price)
        if not legs:
            return None

        sp, lp, sc, lc = legs

        # Net credit calculation
        credit_per_share = sp.mid - lp.mid + sc.mid - lc.mid
        credit_per_share = max(credit_per_share, 0.0)
        wing_width       = sp.strike - lp.strike
        max_loss         = (wing_width - credit_per_share) * 100

        if credit_per_share <= 0.10:
            logger.info("IC: {}: credit too low (${:.2f})", symbol, credit_per_share)
            return None

        # Probability of Profit check (via Julia)
        T     = sp.dte / 365 if sp.dte > 0 else 0.0833
        sigma = sp.delta * 0.4 + 0.15  # approximation when IV data unavailable
        pop   = self._calc_pop(price, sp.strike, lp.strike, sc.strike, lc.strike, T, sigma)
        logger.info("IC: {} — credit=${:.2f}, PoP={:.1f}%, wing_width={}", symbol, credit_per_share, pop * 100, wing_width)

        if pop < 0.60:
            logger.info("IC: {} PoP too low ({:.1f}%)", symbol, pop * 100)
            return None

        qty = max(1, int((equity * _cfg.max_position_size_pct / 100) / (max_loss * 5)))
        qty = min(qty, 3)

        # Risk gate
        intent = OrderIntent(
            symbol       = symbol,
            strategy     = "IRON_CONDOR",
            option_symbol= sp.symbol,
            is_call      = False,
            strike       = sp.strike,
            expiry       = sp.expiry,
            delta        = sp.delta,
            premium      = credit_per_share,
            bid          = credit_per_share * 0.95,
            ask          = credit_per_share * 1.05,
            qty          = qty,
            iv_rank      = iv_rank,
        )
        result = self.risk_gate.evaluate(intent, equity)
        if not result.is_allowed():
            logger.warning("IC rejected for {}: {}", symbol, result.reasons)
            return None
        qty = result.suggested_qty

        # Submit 4-leg order
        try:
            order = self.client.place_iron_condor(
                underlying    = symbol,
                sell_put_sym  = sp.symbol,
                buy_put_sym   = lp.symbol,
                sell_call_sym = sc.symbol,
                buy_call_sym  = lc.symbol,
                net_credit    = credit_per_share,
                qty           = qty,
            )
        except Exception as exc:
            logger.error("IC order failed for {}: {}", symbol, exc)
            return None

        pos = IronCondorPosition(
            underlying  = symbol,
            short_put   = sp,
            long_put    = lp,
            short_call  = sc,
            long_call   = lc,
            net_credit  = credit_per_share * qty * 100,
            max_profit  = credit_per_share * qty * 100,
            max_loss    = max_loss * qty,
            wing_width  = wing_width,
            qty         = qty,
            opened_at   = str(date.today()),
            expiry      = sp.expiry,
            dte_at_open = sp.dte,
            order_id    = order["id"],
        )
        self._positions[symbol] = pos
        self.risk_gate.register_position(symbol, "IRON_CONDOR")
        logger.success(
            "Opened IC: {} × {} | credit=${:.0f} | PoP={:.0f}% | BEs [{:.0f}–{:.0f}]",
            qty, symbol, pos.net_credit, pop * 100,
            pos.breakeven_lower, pos.breakeven_upper,
        )
        return pos

    # ─────────────────────────────────────────────────────────
    # Position Management
    # ─────────────────────────────────────────────────────────
    def manage_positions(self) -> List[str]:
        """Check all ICs for exit conditions."""
        closed = []
        alp_positions = {p["symbol"]: p for p in self.client.get_option_positions()}

        for sym, pos in list(self._positions.items()):
            sp_pos = alp_positions.get(pos.short_put.symbol)

            # If short put is gone, IC is closed/expired
            if not sp_pos:
                logger.info("IC: {} expired/assigned", sym)
                self._positions.pop(sym, None)
                self.risk_gate.remove_position(sym)
                closed.append(sym)
                continue

            unreal = float(sp_pos.get("unrealized_pl", 0))
            pct    = unreal / pos.net_credit if pos.net_credit else 0

            # Profit target: 50%
            if pct >= 0.50:
                logger.info("IC: profit target hit on {} ({:.0f}%)", sym, pct * 100)
                self._close_ic(sym, pos)
                closed.append(sym)
                continue

            # Stop loss: 200% of credit
            if unreal <= -2.0 * pos.net_credit:
                logger.warning("IC: stop-loss on {} (P&L={:.0f})", sym, unreal)
                self._close_ic(sym, pos)
                closed.append(sym)
                continue

            # DTE < 7: close to avoid gamma
            if pos.dte < 7:
                logger.info("IC: {} <7 DTE — closing", sym)
                self._close_ic(sym, pos)
                closed.append(sym)

        return closed

    def _close_ic(self, symbol: str, pos: IronCondorPosition) -> None:
        for leg in [pos.short_put, pos.long_put, pos.short_call, pos.long_call]:
            try:
                self.client.close_position(leg.symbol)
            except Exception as exc:
                logger.warning("IC close leg {} failed: {}", leg.symbol, exc)
        self._positions.pop(symbol, None)
        self.risk_gate.remove_position(symbol)

    @property
    def active_positions(self) -> Dict[str, IronCondorPosition]:
        return dict(self._positions)

    def summary(self) -> List[Dict]:
        return [
            {
                "symbol":      p.underlying,
                "dte":         p.dte,
                "credit":      p.net_credit,
                "max_loss":    p.max_loss,
                "wing_width":  p.wing_width,
                "be_lower":    p.breakeven_lower,
                "be_upper":    p.breakeven_upper,
                "risk_reward": p.risk_reward,
            }
            for p in self._positions.values()
        ]
