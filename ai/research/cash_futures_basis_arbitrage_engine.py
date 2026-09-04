"""
Physical Cash-to-Futures Basis & Storage Arbitrage Engine (Module AV1 - Python)
Synthesizes Carley Garner's "A Trader's First Book on Commodities":
- Local Physical Cash vs. Paper Futures Basis: Basis = Cash Price - Futures Price
- "Strong Basis" vs "Weak Basis" Regime Classification
- Commercial Cash-and-Carry Storage Arbitrage & Full Carrying Charge Convergence
"""

from typing import Dict, List, Any


class CashFuturesBasisArbitrageEngine:
    def __init__(self):
        pass

    def evaluate_basis_regime(
        self,
        local_cash_price: float,
        front_futures_price: float,
        historical_basis_mean: float,
        historical_basis_std: float
    ) -> Dict[str, Any]:
        """
        Basis = Cash Price - Futures Price
        Strong Basis (Cash > Futures or above historical norm): Bullish physical tightness.
        Weak Basis (Cash << Futures or below historical norm): Supply glut / commercial storage capture.
        """
        current_basis = local_cash_price - front_futures_price
        std = max(1e-4, historical_basis_std)
        basis_zscore = (current_basis - historical_basis_mean) / std

        if basis_zscore >= 1.5:
            regime = "STRONG_BASIS_PHYSICAL_SCARCITY"
            commercial_action = "SELL_PHYSICAL_CASH_BUY_FUTURES_HEDGE"
        elif basis_zscore <= -1.5:
            regime = "WEAK_BASIS_STORAGE_OPPORTUNITY"
            commercial_action = "BUY_PHYSICAL_CASH_STORE_SELL_FUTURES_CARRY"
        else:
            regime = "NORMAL_EQUILIBRIUM_BASIS"
            commercial_action = "HOLD_NEUTRAL"

        return {
            "local_cash_price": local_cash_price,
            "front_futures_price": front_futures_price,
            "current_basis": round(current_basis, 2),
            "historical_mean": round(historical_basis_mean, 2),
            "basis_zscore": round(basis_zscore, 2),
            "regime": regime,
            "commercial_action": commercial_action
        }

    def evaluate_cash_and_carry_arbitrage(
        self,
        spot_cash_price: float,
        futures_price: float,
        total_storage_and_interest_cost: float
    ) -> Dict[str, Any]:
        """
        Cash & Carry Arbitrage Profit = Futures Price - Spot Cash Price - Carrying Costs
        """
        gross_spread = futures_price - spot_cash_price
        net_arbitrage_profit = gross_spread - total_storage_and_interest_cost
        is_arbitrage_profitable = net_arbitrage_profit > 0.0

        return {
            "spot_cash_price": spot_cash_price,
            "futures_price": futures_price,
            "gross_spread": round(gross_spread, 2),
            "total_carrying_costs": round(total_storage_and_interest_cost, 2),
            "net_arbitrage_profit": round(net_arbitrage_profit, 2),
            "is_profitable_arbitrage": is_arbitrage_profitable,
            "recommendation": "LOCK_IN_RISKLESS_CARRY_ARBITRAGE" if is_arbitrage_profitable else "CARRY_NOT_VIABLE"
        }
