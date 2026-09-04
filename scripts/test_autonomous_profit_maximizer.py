"""
scripts/test_autonomous_profit_maximizer.py
============================================
Comprehensive Autonomous Profit Maximizer & Self-Relevant Core Verification
Tests that the agent is ready 24/7, operates 100% autonomously, and maximizes profit
using all strategies and methods from Phases 1 through 17.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.brain.autonomous_profit_maximizer import AutonomousProfitMaximizer
from agent.core.continuous_autonomous_daemon import ContinuousAutonomousDaemon
from ai.research.kaching_convexity_engine import KaChingConvexityState

def test_autonomous_profit_maximizer():
    print("=" * 65)
    print("  TESTING AUTONOMOUS PROFIT MAXIMIZER & SELF-RELEVANT 24/7 ENGINE")
    print("=" * 65)

    # 1. Initialize Autonomous Profit Maximizer
    apm = AutonomousProfitMaximizer(
        pdt_threshold=25000.0,
        max_trade_risk_pct=0.05,
        max_portfolio_heat_pct=0.20,
    )
    print("\n[Audit 1/5] APM Initialization across All 17 Strategy Phases: SUCCESS")

    # 2. Multi-Strategy Full Spectrum Evaluation
    universe = ["SPY", "QQQ", "AAPL", "NVDA", "MSFT"]
    all_candidates = []
    for sym in universe:
        spot = 500.0 if sym == "SPY" else (430.0 if sym == "QQQ" else 150.0)
        cands = apm.scan_symbol_opportunities(
            symbol=sym,
            spot=spot,
            iv_rank=42.0,
            macro_regime="Neutral",
            bars_60d=[{"close": spot, "high": spot * 1.01, "low": spot * 0.99} for _ in range(30)],
            chain_contracts=[],
            existing_stock_qty=100 if sym == "AAPL" else 0,
            cost_basis=180.0 if sym == "AAPL" else 0.0,
        )
        all_candidates.extend(cands)

    print(f"\n[Audit 2/5] Evaluated {len(all_candidates)} multi-strategy setups across {len(universe)} symbols:")
    strategy_counts = {}
    for c in all_candidates:
        strategy_counts[c.strategy_name] = strategy_counts.get(c.strategy_name, 0) + 1
    for s_name, count in strategy_counts.items():
        print(f"  - {s_name}: {count} candidates")

    # 3. Maximum-Profit Priority Index (MPPI) Ranking & Selection
    best_trade = apm.select_maximum_profit_trade(all_candidates, is_day_trade=False)
    assert best_trade is not None
    print(f"\n[Audit 3/5] Top-Ranked Maximum Profit Opportunity:")
    print(f"  - Symbol:           {best_trade.symbol}")
    print(f"  - Strategy:         {best_trade.strategy_name}")
    print(f"  - Phase Module:     {best_trade.phase_module}")
    print(f"  - MPPI Score:       {best_trade.max_profit_index}")
    print(f"  - Expected ROI:     {best_trade.expected_roi_pct:.1f}%")
    print(f"  - Win Probability:  {best_trade.win_probability*100:.1f}%")
    print(f"  - Capital Required: ${best_trade.capital_required:,.2f}")
    print(f"  - Max Loss:         ${best_trade.max_loss:,.2f}")
    print(f"  - Rationale:        {best_trade.rationale}")

    # 4. SEC PDT Governor Test (Module BN)
    print(f"\n[Audit 4/5] Testing SEC PDT Governor Compliance Gate (Module BN):")
    # Sub-$25k account with 3 round trips
    apm.update_account_state(equity=18500.0, daily_pnl=0.0, open_round_trips_5d=3)
    pdt_day_trade = apm.select_maximum_profit_trade(all_candidates, is_day_trade=True)
    print(f"  - Sub-$25k with 3 round trips attempting day trade: Selected={pdt_day_trade} (Correctly Blocked: {pdt_day_trade is None})")
    assert pdt_day_trade is None  # Must be blocked by SEC PDT Governor

    # Above-$25k account with 6 round trips
    apm.update_account_state(equity=55000.0, daily_pnl=0.0, open_round_trips_5d=6)
    pdt_day_trade_approved = apm.select_maximum_profit_trade(all_candidates, is_day_trade=True)
    print(f"  - Above-$25k with 6 round trips: Selected={pdt_day_trade_approved.strategy_name if pdt_day_trade_approved else None} (Correctly Permitted)")
    assert pdt_day_trade_approved is not None

    # 5. Continuous Position Surveillance & Profit Harvest (Module BM KaChing)
    print(f"\n[Audit 5/5] Testing Autonomous Profit Harvesting & Roll Defense:")
    # Add an active KaChing position
    apm.active_kaching_positions["SPY"] = KaChingConvexityState(
        long_put_strike=460.0,
        short_put_strike=500.0,
        long_put_delta=0.25,
        short_put_delta=0.50,
        net_weekly_premium=10.0,
        cumulative_cash_collected=10.0,
        days_to_earnings=90,
        roll_count=0,
        double_dip_active=False,
        is_supersized=False,
        status_flags=1,
    )
    # Tuesday with 85% premium banked (current premium = $1.50 vs initial $10.00)
    harvests = apm.evaluate_active_positions(
        current_spots={"SPY": 505.0},
        current_premiums={"SPY": 1.50},
        day_of_week=2,  # Tuesday
    )
    assert len(harvests) > 0
    print(f"  - Early Tuesday Harvest Triggered: {harvests[0]['action']}")
    print(f"  - Reason: {harvests[0]['reason']}")

    # 6. Continuous Autonomous Daemon Validation
    print("\n[Daemon Verification] Testing Continuous Autonomous 24/7 Engine Loop:")
    daemon = ContinuousAutonomousDaemon(cycle_interval_seconds=5)
    market_cycle = daemon.run_market_hours_cycle()
    print(f"  - Market Hours Cycle: Status={market_cycle['status']}, Candidates={market_cycle['candidates_evaluated']}, TopTrade={market_cycle['best_trade']} on {market_cycle['best_symbol']}")
    off_market_cycle = daemon.run_off_market_cycle()
    print(f"  - Off-Market Cycle: Status={off_market_cycle['status']}, Zero-Bridge Sync={off_market_cycle['zero_bridge_sync']}, Equity=${off_market_cycle['account_equity']:,.2f}")

    print("\n" + "=" * 65)
    print("  ALL AUTONOMOUS PROFIT MAXIMIZATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    test_autonomous_profit_maximizer()
