"""
Module BL1: Fundamental SEC Financials Sentinel, Ratio Stock Repair & Volatility Routing Engine
Synthesized from Michael K Brown's 'Mastering Stocks 2020' & David Jaffee's 'Options Trading Beginners Guide'.
"""

from typing import Dict, Any

class FundamentalStockRepairEngine:
    def __init__(self, min_cash_reserve_pct: float = 40.0):
        self.min_cash_reserve_pct = min_cash_reserve_pct

    def calculate_valuation_ratios(
        self,
        stock_price: float,
        eps: float,
        eps_growth_pct: float,
        sales_per_share: float,
        total_debt: float,
        total_assets: float
    ) -> Dict[str, Any]:
        pe = stock_price / max(0.01, eps) if eps > 0 else -1.0
        peg = (pe / eps_growth_pct) if (eps_growth_pct > 0 and pe > 0) else -1.0
        psr = stock_price / max(0.01, sales_per_share)
        debt_ratio = total_debt / max(0.01, total_assets)

        is_undervalued = (0 < pe < 20.0) and (0 < peg < 1.0) and (psr < 3.0)
        debt_alarm = debt_ratio > 1.0

        return {
            "pe_ratio": round(pe, 2) if pe > 0 else None,
            "peg_ratio": round(peg, 3) if peg > 0 else None,
            "price_to_sales": round(psr, 2),
            "debt_to_assets_ratio": round(debt_ratio, 3),
            "is_undervalued": is_undervalued,
            "debt_alarm": debt_alarm,
            "fundamental_grade": "SAFE_VALUE" if (is_undervalued and not debt_alarm) else "HIGH_RISK_AVOID"
        }

    def calculate_stock_repair_strategy(
        self,
        current_stock_price: float,
        original_cost_basis: float,
        shares_held: int = 100
    ) -> Dict[str, Any]:
        drop_pct = ((original_cost_basis - current_stock_price) / original_cost_basis) * 100.0
        is_candidate = 15.0 <= drop_pct <= 25.0

        long_call_strike = current_stock_price
        half_loss = (original_cost_basis - current_stock_price) / 2.0
        short_call_strike = current_stock_price + half_loss

        return {
            "current_price": current_stock_price,
            "cost_basis": original_cost_basis,
            "drawdown_pct": round(drop_pct, 2),
            "is_repair_candidate": is_candidate,
            "buy_1x_long_call_strike": round(long_call_strike, 2),
            "sell_2x_short_call_strike": round(short_call_strike, 2),
            "breakeven_recovery_price": round(short_call_strike, 2),
            "action": "EXECUTE_1X2_RATIO_REPAIR" if is_candidate else "NOT_RECOMMENDED_FOR_REPAIR"
        }

    def route_volatility_trade_regime(
        self,
        vix_level: float,
        current_time_minutes_to_close: int,
        portfolio_cash_pct: float
    ) -> Dict[str, Any]:
        cash_safe = portfolio_cash_pct >= self.min_cash_reserve_pct
        in_eod_execution_window = current_time_minutes_to_close <= 60

        if vix_level >= 20.0:
            recommended_strategy = "NAKED_OTM_PREMIUM_HARVEST"
            reason = "VIX >= 20 indicates rich implied volatility; maximize premium collected."
        else:
            recommended_strategy = "VERTICAL_CREDIT_SPREADS"
            reason = "VIX < 20 leaves higher risk of volatility expansion; enforce defined-risk protection."

        return {
            "vix_level": vix_level,
            "recommended_strategy": recommended_strategy,
            "reason": reason,
            "cash_reserve_pct": portfolio_cash_pct,
            "cash_buffer_compliant": cash_safe,
            "is_eod_window": in_eod_execution_window,
            "trade_permission": "APPROVED" if (cash_safe and in_eod_execution_window) else "DEFERRED_WAIT_FOR_EOD_OR_CASH"
        }