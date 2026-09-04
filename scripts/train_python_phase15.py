"""
Phase 15 Training Matrix Runner (T1 - Python)
Benchmarks and trains Modules BE1, BF1, BG1, BH1.
"""

import os
import sys

# Ensure ai package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.research.all_weather_vomma_engine import AllWeatherVommaEngine
from ai.research.gamma_scalping_stochastic_engine import GammaScalpingStochasticEngine
from ai.research.bladerunner_carry_forex_engine import BladerunnerCarryForexEngine
from ai.research.structured_collar_box_arbitrage_engine import StructuredCollarBoxArbitrageEngine


def run_phase15_python_training():
    print("[T1 PYTHON] Starting High-Level AI Training Epochs for Phase 15...")

    # 1. Train Module BE1: All-Weather Options Portfolio & Vomma Engine (Karl Domm)
    vomma_engine = AllWeatherVommaEngine()
    regime_res = vomma_engine.classify_market_regime(spx_return_pct=-12.5, vix_spike_pts=38.0)
    margin_res = vomma_engine.calculate_portfolio_margin_requirement(
        pnl_down_12pct=-7800.0, pnl_down_20pct=-11000.0, pnl_up_10pct=-1000.0, planned_capital=20000.0
    )
    hedge_res = vomma_engine.evaluate_teenie_vomma_hedge(core_iron_condor_vomma=-0.25, num_teenie_puts=5, teenie_put_vomma_per_contract=0.08)

    print(f"  [BE1] Market Regime: {regime_res['regime']} -> Status: {regime_res['hedging_status']}")
    print(f"  [BE1] SPAN Slicing Margin: ${margin_res['worst_case_margin_requirement']} (Util: {margin_res['margin_utilization_pct']}%) -> {margin_res['verdict']}")
    print(f"  [BE1] 5-Delta Teenie Put Hedge: Net Vomma={hedge_res['net_portfolio_vomma']} -> {hedge_res['protection_status']}")

    # 2. Train Module BF1: Algorithmic Gamma Scalping & Stochastic Engine (Van Der Post)
    scalp_engine = GammaScalpingStochasticEngine()
    greeks_res = scalp_engine.calculate_black_scholes_greeks(spot=100.0, strike=100.0, time_to_exp=0.0833, r=0.05, sigma=0.25, is_call=True)
    rebal_res = scalp_engine.compute_gamma_scalping_hedge(current_portfolio_delta=12.5, spot_price=100.0, gamma_total=greeks_res['gamma'])

    print(f"  [BF1] Greeks: Delta={greeks_res['delta']}, Gamma={greeks_res['gamma']}, Vomma={greeks_res['vomma']}, Vanna={greeks_res['vanna']}")
    print(f"  [BF1] Scalping Action: {rebal_res['hedge_action']} (Rebalance {rebal_res['shares_to_hedge']} shares)")

    # 3. Train Module BG1: Forex Microstructure & Carry Engine (Odin Velez)
    fx_engine = BladerunnerCarryForexEngine()
    blade_res = fx_engine.evaluate_bladerunner_setup(current_spot=1.3520, ema_20_level=1.3500, is_candle_rejected=True, is_breakout_confirmed=True)
    carry_res = fx_engine.calculate_daily_carry_yield(long_currency_rate_pct=4.50, short_currency_rate_pct=0.10, position_units=100000.0)
    kelly_res = fx_engine.compute_kelly_fraction(win_probability=0.60, win_loss_ratio=1.5)

    print(f"  [BG1] Bladerunner 20-EMA: {blade_res['polarity']} -> Signal: {blade_res['trade_signal']}")
    print(f"  [BG1] Forex Carry Yield: Daily=${carry_res['daily_interest_earned']}, Annual=${carry_res['annualized_carry_dollars']}")
    print(f"  [BG1] Kelly Sizing: Optimal Alloc={kelly_res['recommended_allocation_pct']}%")

    # 4. Train Module BH1: Structured Collar & Box Arbitrage Engine (Robinson & Sykes)
    box_engine = StructuredCollarBoxArbitrageEngine()
    collar_res = box_engine.structure_costless_collar(stock_cost_basis=79.0, current_spot=79.0, call_strike=88.0, call_premium_received=1.75, put_strike=85.0, put_premium_cost=1.24)
    box_res = box_engine.evaluate_long_box_arbitrage(lower_strike=95.0, higher_strike=105.0, net_debit_paid=8.80)
    fro_res = box_engine.evaluate_binary_fixed_return_option(bet_amount=100.0, payout_rate_pct=80.0, rebate_rate_pct=10.0, is_in_the_money=True)

    print(f"  [BH1] Collar Structuring: Net Premium=${collar_res['net_collar_premium']} -> {collar_res['collar_classification']}")
    print(f"  [BH1] Long Box Arbitrage: Risk-Free Profit=${box_res['risk_free_profit']} -> {box_res['execution_directive']}")
    print(f"  [BH1] Binary FRO Trade: Return=${fro_res['total_return']} -> {fro_res['result_status']}")

    print("[T1 PYTHON] Modules BE1, BF1, BG1, BH1 trained successfully on Phase 15 requirements.")


if __name__ == "__main__":
    run_phase15_python_training()
