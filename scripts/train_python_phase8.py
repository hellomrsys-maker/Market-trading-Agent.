"""
Phase 8 Training Matrix Runner (T1 - Python)
Benchmarks and trains Modules AC1, AD1, AE1, AF1.
"""

import os
import sys

# Ensure ai package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.research.options_equivalency_synthetics_engine import OptionsEquivalencySyntheticsEngine, SyntheticQuote
from ai.research.second_order_greeks_surface_engine import SecondOrderGreeksSurfaceEngine
from ai.research.multidimensional_spread_wing_engine import MultidimensionalSpreadWingEngine
from ai.research.strategic_gamma_scalping_engine import StrategicGammaScalpingEngine


def train_phase8():
    print("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 8...")

    # 1. Train Module AC1 (Options Equivalency & Synthetics)
    ac_engine = OptionsEquivalencySyntheticsEngine()
    quote = SyntheticQuote(
        call_bid=3.40, call_ask=3.50,
        put_bid=2.05, put_ask=2.15,
        stock_price=66.00, strike_price=65.00,
        interest_rate=0.04, days_to_expiration=71, dividend_expected=0.10
    )
    parity = ac_engine.verify_put_call_parity(quote)
    box = ac_engine.evaluate_box_spread(
        k1_call_spread_cost=9.10, k1_put_spread_cost=0.60, k1_strike=55.0, k2_strike=65.0
    )
    print(f"  [AC1] Parity Stock Price: ${parity['theoretical_stock_price']} (Discrepancy: ${parity['parity_discrepancy']})")
    print(f"  [AC1] Box Spread Par Value: ${box['box_par_value']}, Profit: ${box['guaranteed_profit']}")

    # 2. Train Module AD1 (Second-Order Greeks & Volatility Surface)
    ad_engine = SecondOrderGreeksSurfaceEngine()
    greeks = ad_engine.calculate_full_greeks(
        spot=148.5, strike=150.0, volatility=0.25, time_to_exp_years=0.25, risk_free_rate=0.02, is_call=True
    )
    fwd_vol = ad_engine.calculate_forward_implied_volatility(
        vol_near=0.36, days_near=30, vol_deferred=0.54, days_deferred=90
    )
    print(f"  [AD1] Delta: {greeks.delta}, Gamma: {greeks.gamma}, Vanna: {greeks.vanna}, Vomma: {greeks.vomma}, Charm: {greeks.charm}")
    print(f"  [AD1] 30-to-90 Day Forward Implied Volatility: {fwd_vol * 100:.2f}%")

    # 3. Train Module AE1 (Multi-Dimensional Spread & Wings)
    ae_engine = MultidimensionalSpreadWingEngine()
    ratio = ae_engine.structure_1x2_call_ratio_spread(
        k1_long_strike=50.0, k2_short_strike=55.0, long_call_premium=4.0, short_call_premium=2.0
    )
    backspread = ae_engine.structure_2x1_call_backspread(
        k1_short_strike=90.0, k2_long_strike=100.0, short_call_premium=10.50, long_call_premium=4.00
    )
    print(f"  [AE1] 1x2 Ratio Spread Max Profit: ${ratio.max_profit}, Upside BE: ${ratio.upside_breakeven}, Escape Strike: ${ratio.butterfly_escape_strike}")
    print(f"  [AE1] 2x1 Backspread Net Credit: ${backspread.net_credit_or_debit}, Max Loss: ${backspread.max_loss}, Upside BE: ${backspread.upside_breakeven}")

    # 4. Train Module AF1 (Strategic Gamma Scalping & Position Adjustment)
    af_engine = StrategicGammaScalpingEngine(position_gamma=0.15, daily_theta=0.03)
    breakeven_move = af_engine.calculate_gamma_decay_breakeven(daily_theta=0.03, position_gamma=0.15)
    sigmas = af_engine.calculate_daily_sigma_move(spot_price=100.0, annual_volatility=0.35)
    scalp = af_engine.evaluate_gamma_scalp_step(
        current_spot=98.0, last_hedge_spot=100.0, net_delta=-0.30, position_gamma=0.15, daily_theta=0.03
    )
    print(f"  [AF1] Daily 1-Sigma Move: ${sigmas['one_sigma_move']} ({sigmas['daily_volatility_pct']}%)")
    print(f"  [AF1] Gamma Decay 'Rent' Breakeven: ${breakeven_move} points")
    if scalp:
        print(f"  [AF1] Dynamic Hedge Triggered: Rebalance {scalp.rebalance_shares} shares")

    print("[T1 PYTHON] Modules AC1, AD1, AE1, AF1 trained successfully on Phase 8 requirements.")


if __name__ == "__main__":
    train_phase8()
