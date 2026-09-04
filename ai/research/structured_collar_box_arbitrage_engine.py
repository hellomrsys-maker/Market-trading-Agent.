"""
Structured Options, Collars & Binary Box Arbitrage Engine (Module BH1 - Python)
Synthesizes Charles Robinson's "Covered Calls" & Jordon Sykes's "Binary Options":
- Covered Call Yield & Costless Collar Structuring: Call Premium Received == Put Premium Paid
- Fixed Return Options (FRO) Binary Payout Modeling (70-85% ITM vs 0-15% OTM)
- Risk-Free Long Box Arbitrage: Box Expiration Value - Net Premium Paid > 0
"""

from typing import Dict, List, Any


class StructuredCollarBoxArbitrageEngine:
    def __init__(self):
        pass

    def structure_costless_collar(
        self,
        stock_cost_basis: float,
        current_spot: float,
        call_strike: float,
        call_premium_received: float,
        put_strike: float,
        put_premium_cost: float
    ) -> Dict[str, Any]:
        """
        Costless Collar: Call Premium Received >= Put Premium Cost.
        """
        net_credit_debit = call_premium_received - put_premium_cost
        is_costless = net_credit_debit >= 0.0

        max_upside_profit = (call_strike - stock_cost_basis) + net_credit_debit
        max_downside_loss = (stock_cost_basis - put_strike) - net_credit_debit

        return {
            "stock_cost_basis": stock_cost_basis,
            "call_strike": call_strike,
            "put_strike": put_strike,
            "net_collar_premium": round(net_credit_debit, 2),
            "is_costless_or_better": is_costless,
            "max_upside_profit": round(max_upside_profit, 2),
            "max_downside_risk": round(max_downside_loss, 2),
            "collar_classification": "ZERO_COST_HEDGED_COLLAR" if is_costless else "NET_DEBIT_PROTECTIVE_COLLAR"
        }

    def evaluate_long_box_arbitrage(
        self,
        lower_strike: float,
        higher_strike: float,
        net_debit_paid: float
    ) -> Dict[str, Any]:
        """
        Long Box Arbitrage = Long Call (K1) + Short Call (K2) + Long Put (K2) + Short Put (K1)
        Guaranteed Expiration Payoff = Higher Strike - Lower Strike.
        Risk-Free Profit = Payoff - Net Debit Paid.
        """
        box_expiration_value = higher_strike - lower_strike
        risk_free_profit = box_expiration_value - net_debit_paid
        is_arbitrage_profitable = risk_free_profit > 0.0

        return {
            "lower_strike": lower_strike,
            "higher_strike": higher_strike,
            "box_expiration_value": round(box_expiration_value, 2),
            "net_debit_paid": round(net_debit_paid, 2),
            "risk_free_profit": round(risk_free_profit, 2),
            "is_arbitrage_profitable": is_arbitrage_profitable,
            "execution_directive": "EXECUTE_RISKLESS_BOX_ARBITRAGE" if is_arbitrage_profitable else "NO_ARBITRAGE_MISPRICING"
        }

    def evaluate_binary_fixed_return_option(
        self,
        bet_amount: float,
        payout_rate_pct: float,
        rebate_rate_pct: float,
        is_in_the_money: bool
    ) -> Dict[str, Any]:
        """
        Binary Digital Fixed Return Option:
        ITM: Bet * (1 + Payout %)
        OTM: Bet * Rebate %
        """
        if is_in_the_money:
            total_return = bet_amount * (1.0 + payout_rate_pct / 100.0)
            net_profit = bet_amount * (payout_rate_pct / 100.0)
        else:
            total_return = bet_amount * (rebate_rate_pct / 100.0)
            net_profit = total_return - bet_amount

        return {
            "bet_amount": bet_amount,
            "is_in_the_money": is_in_the_money,
            "total_return": round(total_return, 2),
            "net_profit": round(net_profit, 2),
            "result_status": "WIN_IN_THE_MONEY" if is_in_the_money else "LOSS_OUT_OF_THE_MONEY"
        }
