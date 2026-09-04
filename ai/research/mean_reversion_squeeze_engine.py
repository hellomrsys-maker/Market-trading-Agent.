"""
Module BI1: Mean Reversion, Squeeze Detection & Dynamic PNR Boundary Governor
Synthesized from Nishant Pant's 'Mean Reversion Trading: Using Options Spreads and Technical Analysis'.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np

@dataclass
class PNRStatus:
    long_strike: float
    short_strike: float
    days_to_expiration: int
    current_atr: float
    pnr_threshold: float
    current_underlying_price: float
    is_pnr_breached: bool
    should_cut_50pct_loss: bool

class MeanReversionSqueezeEngine:
    def __init__(self, max_portfolio_allocation_pct: float = 30.0, cash_reserve_pct: float = 70.0):
        self.max_allocation_pct = max_portfolio_allocation_pct
        self.cash_reserve_pct = cash_reserve_pct

    def evaluate_ttm_squeeze(
        self,
        closes: List[float],
        highs: List[float],
        lows: List[float],
        bb_period: int = 20,
        bb_mult: float = 2.0,
        kc_period: int = 20,
        kc_atr_mult: float = 1.5
    ) -> Dict[str, Any]:
        if len(closes) < max(bb_period, kc_period):
            return {"status": "INSUFFICIENT_DATA", "is_squeeze_active": False}

        recent_closes = np.array(closes[-bb_period:])
        sma = np.mean(recent_closes)
        std = np.std(recent_closes)
        bb_upper = sma + (bb_mult * std)
        bb_lower = sma - (bb_mult * std)

        tr_list = []
        for i in range(len(closes) - kc_period, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]) if i > 0 else highs[i] - lows[i],
                abs(lows[i] - closes[i - 1]) if i > 0 else highs[i] - lows[i]
            )
            tr_list.append(tr)
        atr = float(np.mean(tr_list))

        kc_upper = sma + (kc_atr_mult * atr)
        kc_lower = sma - (kc_atr_mult * atr)

        is_squeeze = (bb_upper < kc_upper) and (bb_lower > kc_lower)
        current_price = closes[-1]
        is_touching_upper = current_price >= bb_upper
        is_touching_lower = current_price <= bb_lower

        return {
            "sma_20": round(float(sma), 2),
            "bb_upper": round(float(bb_upper), 2),
            "bb_lower": round(float(bb_lower), 2),
            "kc_upper": round(float(kc_upper), 2),
            "kc_lower": round(float(kc_lower), 2),
            "atr": round(atr, 2),
            "is_squeeze_active": bool(is_squeeze),
            "is_touching_upper_band": bool(is_touching_upper),
            "is_touching_lower_band": bool(is_touching_lower),
            "trade_permission": "HOLD_SQUEEZE_COILING" if is_squeeze else "PERMITTED_FOR_MEAN_REVERSION"
        }

    def evaluate_momentum_filter(
        self,
        current_adx: float,
        adx_slope_up: bool,
        di_plus: float,
        di_minus: float,
        current_rsi: float,
        previous_rsi: float,
        trade_bias: str = "BULLISH"
    ) -> Dict[str, Any]:
        adx_blocks_contrarian = (current_adx > 40.0) and adx_slope_up
        dmi_crossover = (di_plus > di_minus) if trade_bias == "BULLISH" else (di_minus > di_plus)
        
        rsi_exhausted = False
        if trade_bias == "BULLISH":
            rsi_exhausted = (previous_rsi <= 35.0) and (current_rsi > previous_rsi)
        else:
            rsi_exhausted = (previous_rsi >= 65.0) and (current_rsi < previous_rsi)

        signal_valid = (not adx_blocks_contrarian) and (dmi_crossover or rsi_exhausted)

        return {
            "adx_value": current_adx,
            "adx_blocks_contrarian": adx_blocks_contrarian,
            "dmi_alignment": "BULLISH" if di_plus > di_minus else "BEARISH",
            "rsi_exhaustion_confirmed": rsi_exhausted,
            "momentum_confirmation": "CONFIRMED" if signal_valid else "BLOCKED_BY_MOMENTUM"
        }

    def calculate_pnr(
        self,
        long_strike: float,
        short_strike: float,
        days_to_expiration: int,
        current_atr: float,
        current_price: float,
        spread_type: str = "BULL_CALL"
    ) -> PNRStatus:
        pnr_offset = (long_strike * days_to_expiration * current_atr) / 2000.0
        
        if spread_type in ["BULL_CALL", "BULL_PUT"]:
            pnr_threshold = long_strike - pnr_offset
            is_breached = current_price < pnr_threshold
        else:
            pnr_threshold = long_strike + pnr_offset
            is_breached = current_price > pnr_threshold

        should_cut = is_breached or (days_to_expiration < 15 and is_breached)

        return PNRStatus(
            long_strike=long_strike,
            short_strike=short_strike,
            days_to_expiration=days_to_expiration,
            current_atr=current_atr,
            pnr_threshold=round(pnr_threshold, 2),
            current_underlying_price=current_price,
            is_pnr_breached=is_breached,
            should_cut_50pct_loss=should_cut
        )

    def audit_portfolio_exposure(
        self,
        total_net_liquidation: float,
        currently_deployed_capital: float,
        is_correction_mode: bool = False
    ) -> Dict[str, Any]:
        max_allowed_pct = 60.0 if is_correction_mode else self.max_allocation_pct
        max_deployable_dollars = (max_allowed_pct / 100.0) * total_net_liquidation
        available_budget = max(0.0, max_deployable_dollars - currently_deployed_capital)
        current_utilization_pct = (currently_deployed_capital / max(1.0, total_net_liquidation)) * 100.0

        return {
            "net_liquidation": total_net_liquidation,
            "deployed_capital": currently_deployed_capital,
            "utilization_pct": round(current_utilization_pct, 2),
            "max_allowed_utilization_pct": max_allowed_pct,
            "available_budget_for_new_trades": round(available_budget, 2),
            "cash_reserve_preserved": round(total_net_liquidation - currently_deployed_capital, 2),
            "allocation_approved": current_utilization_pct <= max_allowed_pct
        }