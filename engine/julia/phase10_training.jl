# Phase 10 Training Matrix Runner (T5 - Julia)
# Benchmarks Modules AK5, AL5, AM5, AN5

include("schwager_price_action_engine.jl")
include("commodity_spread_arbitrage_engine.jl")
include("cot_institutional_sentiment_engine.jl")
include("futures_risk_governor_engine.jl")

using .SchwagerPriceActionEngine
using .CommoditySpreadArbitrageEngine
using .CotInstitutionalSentimentEngine
using .FuturesRiskGovernorEngine

println("[T5 JULIA] Starting Quantitative Futures Microstructure & Spread Simulation for Phase 10...")

# 1. Train AK5
pa_res = evaluate_key_reversal(98.0, 102.0, 99.0, 97.0, 103.5, 103.0, 150000.0, 100000.0)

# 2. Train AL5
crack_res = compute_crack_321(75.0, 2.45, 2.65)

# 3. Train AM5
cot_res = calculate_cot_index(185000.0, 20000.0, 200000.0)

# 4. Train AN5
risk_res = calculate_atr_position(100000.0, 1.5, 2.25, 2.0, 1000.0)

println("[T5 JULIA] Modules AK5, AL5, AM5, AN5 trained successfully.")
