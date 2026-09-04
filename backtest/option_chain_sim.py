"""
backtest/option_chain_sim.py
=============================
OptionAlpha Agent — Realistic Synthetic Option Chain Generator

Generates realistic option chains (strikes, bids, asks, deltas, gammas, thetas, vegas)
using Black-Scholes-Merton with an empirical volatility skew (smile) model.
Used by the Backtesting engine when historical option tick data is unavailable.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Dict, List, Optional
from scipy.stats import norm


def bsm_price(
    spot: float,
    strike: float,
    dte: int,
    iv: float,
    r: float = 0.05,
    is_call: bool = True
) -> float:
    """Standard Black-Scholes-Merton formula."""
    if dte <= 0:
        if is_call:
            return max(0.0, spot - strike)
        else:
            return max(0.0, strike - spot)

    T = dte / 365.0
    sigma = max(iv, 0.01)
    d1 = (math.log(spot / strike) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if is_call:
        price = spot * norm.cdf(d1) - strike * math.exp(-r * T) * norm.cdf(d2)
    else:
        price = strike * math.exp(-r * T) * norm.cdf(-d2) - spot * norm.cdf(-d1)

    return max(0.01, price)


def bsm_greeks(
    spot: float,
    strike: float,
    dte: int,
    iv: float,
    r: float = 0.05,
    is_call: bool = True
) -> Dict[str, float]:
    """Calculate Delta, Gamma, Theta, Vega under BSM."""
    if dte <= 0:
        delta = 1.0 if (is_call and spot > strike) or (not is_call and spot < strike) else 0.0
        if not is_call and spot < strike:
            delta = -1.0
        return {"delta": delta, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

    T = dte / 365.0
    sigma = max(iv, 0.01)
    d1 = (math.log(spot / strike) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    pdf_d1 = norm.pdf(d1)

    if is_call:
        delta = norm.cdf(d1)
        theta = (-spot * pdf_d1 * sigma / (2 * math.sqrt(T)) - r * strike * math.exp(-r * T) * norm.cdf(d2)) / 365.0
    else:
        delta = norm.cdf(d1) - 1.0
        theta = (-spot * pdf_d1 * sigma / (2 * math.sqrt(T)) + r * strike * math.exp(-r * T) * norm.cdf(-d2)) / 365.0

    gamma = pdf_d1 / (spot * sigma * math.sqrt(T))
    vega = spot * math.sqrt(T) * pdf_d1 / 100.0  # per 1% vol change

    return {
        "delta": round(delta, 4),
        "gamma": round(gamma, 5),
        "theta": round(theta, 4),
        "vega": round(vega, 4),
    }


class OptionChainSimulator:
    """
    Simulates full option chains with quadratic volatility smile / skew
    and realistic bid-ask spread models based on moneyness.
    """

    def __init__(self, risk_free_rate: float = 0.05):
        self.r = risk_free_rate

    def generate_chain(
        self,
        symbol: str,
        spot: float,
        atm_iv: float,
        target_dtes: Optional[List[int]] = None,
        strike_spacing_pct: float = 0.01,  # 1% intervals
        num_strikes: int = 21,             # 10 OTM, 1 ATM, 10 ITM
        current_date: Optional[date] = None,
    ) -> List[Dict]:
        """
        Generate synthetic option contracts matching Alpaca option chain structure.
        """
        target_dtes = target_dtes or [21, 30, 45]
        today = current_date or date.today()
        contracts = []

        # Round base ATM strike to reasonable intervals (e.g. nearest $1, $2.5, or $5)
        if spot > 300:
            base_strike = round(spot / 5.0) * 5.0
            step = 5.0
        elif spot > 100:
            base_strike = round(spot / 2.5) * 2.5
            step = 2.5
        else:
            base_strike = round(spot / 1.0) * 1.0
            step = 1.0

        half_n = num_strikes // 2
        strikes = [base_strike + (i - half_n) * step for i in range(num_strikes)]
        strikes = [s for s in strikes if s > 0]

        for dte in target_dtes:
            expiry_date = today + timedelta(days=dte)
            expiry_str = expiry_date.strftime("%Y-%m-%d")

            for strike in strikes:
                # Quadratic volatility skew model: OTM puts get higher IV, OTM calls slightly lower
                k = math.log(strike / spot)
                skew_adjustment = -0.15 * k + 0.35 * (k ** 2)
                local_iv = max(0.05, atm_iv + skew_adjustment)

                for is_call in [True, False]:
                    contract_type = "call" if is_call else "put"
                    theo_price = bsm_price(spot, strike, dte, local_iv, self.r, is_call)
                    greeks = bsm_greeks(spot, strike, dte, local_iv, self.r, is_call)

                    # Bid-ask spread model: 2% to 8% depending on distance from ATM
                    moneyness = abs(k)
                    spread_pct = min(0.12, max(0.02, 0.02 + 0.05 * moneyness))
                    spread = max(0.05, theo_price * spread_pct)

                    bid = max(0.01, round(theo_price - spread / 2.0, 2))
                    ask = max(bid + 0.01, round(theo_price + spread / 2.0, 2))
                    mid = round((bid + ask) / 2.0, 2)

                    # Symbol format matching OCC standard e.g. SPY250620P00480000
                    exp_sym = expiry_date.strftime("%y%m%d")
                    type_sym = "C" if is_call else "P"
                    strike_sym = f"{int(strike * 1000):08d}"
                    occ_symbol = f"{symbol}{exp_sym}{type_sym}{strike_sym}"

                    contracts.append({
                        "symbol": occ_symbol,
                        "underlying": symbol,
                        "strike": strike,
                        "expiration_date": expiry_str,
                        "dte": dte,
                        "type": contract_type,
                        "is_call": is_call,
                        "bid": bid,
                        "ask": ask,
                        "mid": mid,
                        "close_price": mid,
                        "implied_volatility": round(local_iv, 4),
                        "delta": greeks["delta"],
                        "gamma": greeks["gamma"],
                        "theta": greeks["theta"],
                        "vega": greeks["vega"],
                        "open_interest": int(max(50, 2000 * math.exp(-3 * abs(k)))),
                        "volume": int(max(10, 500 * math.exp(-3 * abs(k)))),
                    })

        return contracts
