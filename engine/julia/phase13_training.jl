# Phase 13 Training Matrix Runner (T5 - Julia)
# Benchmarks Modules AW5, AX5, AY5, AZ5

include("volatility_edge_discovery_engine.jl")
include("trading_firm_greek_governor.jl")
include("volatility_skew_arbitrage_engine.jl")
include("trade_adjustment_repair_engine.jl")

using .VolatilityEdgeDiscoveryEngine
using .TradingFirmGreekGovernor
using .VolatilitySkewArbitrageEngine
using .TradeAdjustmentRepairEngine

println("[T5 JULIA] Starting Trading Firm Greek Inventory & Skew Simulation for Phase 13...")

# 1. Train AW5
vol_res = evaluate_edge(24.5, 18.2, 14.0, 32.0)

# 2. Train AX5
greek_res = audit_inventory(15.0, 0.04, -25.0, 35.0, 100.0, 0.25, 100000.0)

# 3. Train AY5
skew_res = evaluate_skew(20.0, 26.5, 19.0, 20.0, 22.0)
bwb_res = structure_bwb(90.0, 95.0, 98.0, 1.20, 2.10, 2.80)

# 4. Train AZ5
repair_res = audit_defense(-180.0, 150.0, -0.38, 18.0, 0.65)

println("[T5 JULIA] Modules AW5, AX5, AY5, AZ5 trained successfully.")
