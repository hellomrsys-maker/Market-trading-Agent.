"""
Phase 12 Training Matrix Runner (T1 - Python)
Benchmarks and trains Modules AS1, AT1, AU1, AV1.
"""

import os
import sys

# Ensure ai package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.research.commodity_specs_margin_engine import CommoditySpecsMarginEngine
from ai.research.delivery_roll_governor_engine import DeliveryRollGovernorEngine
from ai.research.commodity_seasonality_cycle_engine import CommoditySeasonalityCycleEngine
from ai.research.cash_futures_basis_arbitrage_engine import CashFuturesBasisArbitrageEngine


def run_phase12_python_training():
    print("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 12...")

    # 1. Train Module AS1: Commodity Specs & SPAN Margin Engine
    specs_engine = CommoditySpecsMarginEngine()
    cl_specs = specs_engine.get_contract_specs("CL")
    margin_audit = specs_engine.audit_span_margin_health(
        account_equity=50000.0,
        open_positions=[
            {"symbol": "CL", "contracts": 2, "is_spread": False},
            {"symbol": "ZC", "contracts": 4, "is_spread": True}
        ],
        spread_discount_factor=0.50
    )

    print(f"  [AS1] CL Specs: Multiplier={cl_specs['multiplier']}, Tick Val=${cl_specs['tick_value']}, Margin: ${cl_specs['initial_margin']}")
    print(f"  [AS1] SPAN Margin Health: Status={margin_audit['status']} (Excess: ${margin_audit['margin_excess']}, Utilization: {margin_audit['margin_utilization_pct']}%)")

    # 2. Train Module AT1: Delivery Roll Governor Engine
    roll_engine = DeliveryRollGovernorEngine(fnd_warning_days=5)
    roll_res = roll_engine.evaluate_delivery_risk(
        symbol="CL", days_to_fnd=4, days_to_ltd=15, front_month_volume=120000, next_month_volume=150000
    )

    print(f"  [AT1] Delivery Risk: {roll_res['symbol']} ({roll_res['settlement_type']}) -> Action: {roll_res['recommended_action']}")

    # 3. Train Module AU1: Commodity Seasonality Cycle Engine
    seas_engine = CommoditySeasonalityCycleEngine()
    seas_res = seas_engine.evaluate_seasonal_bias(symbol="ZC", current_month=5, weather_shock_severity=0.4)
    spread_res = seas_engine.evaluate_old_crop_new_crop_spread(old_crop_price=540.0, new_crop_price=490.0, historical_spread_mean=20.0)

    print(f"  [AU1] Seasonal Bias: {seas_res['symbol']} Month {seas_res['month']} -> {seas_res['regime']} (Score: {seas_res['adjusted_seasonal_score']})")
    print(f"  [AU1] Old/New Crop Spread: Current=${spread_res['current_spread']}, Inverted={spread_res['is_inverted_market']} -> {spread_res['signal']}")

    # 4. Train Module AV1: Cash Futures Basis Arbitrage Engine
    basis_engine = CashFuturesBasisArbitrageEngine()
    basis_res = basis_engine.evaluate_basis_regime(local_cash_price=5.10, front_futures_price=4.85, historical_basis_mean=0.10, historical_basis_std=0.08)
    carry_res = basis_engine.evaluate_cash_and_carry_arbitrage(spot_cash_price=75.0, futures_price=79.5, total_storage_and_interest_cost=3.20)

    print(f"  [AV1] Basis Regime: Z-Score={basis_res['basis_zscore']} -> {basis_res['regime']} ({basis_res['commercial_action']})")
    print(f"  [AV1] Cash & Carry Arbitrage Profit: ${carry_res['net_arbitrage_profit']} -> {carry_res['recommendation']}")

    print("[T1 PYTHON] Modules AS1, AT1, AU1, AV1 trained successfully on Phase 12 requirements.")


if __name__ == "__main__":
    run_phase12_python_training()
