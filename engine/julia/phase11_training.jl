# Phase 11 Training Matrix Runner (T5 - Julia)
# Benchmarks Modules AO5, AP5, AQ5, AR5

include("cash_secured_put_engine.jl")
include("covered_call_yield_engine.jl")
include("wheel_strategy_engine.jl")
include("retail_income_risk_governor.jl")

using .CashSecuredPutEngine
using .CoveredCallYieldEngine
using .WheelStrategyEngine
using .RetailIncomeRiskGovernor

println("[T5 JULIA] Starting Retail-to-Institutional Income & Wheel Simulation for Phase 11...")

# 1. Train AO5
csp_res = evaluate_csp(100.0, 95.0, 1.85, 35.0, -0.26)

# 2. Train AP5
cc_res = evaluate_covered_call(100.0, 102.5, 105.0, 2.40, 30.0, 0.50)

# 3. Train AQ5
wheel_res = track_wheel(2, 98.0, 100.0, 3.50, 2.10, 1.00, 95.0, 2.00, 0.80)

# 4. Train AR5
risk_res = audit_trade(100000.0, 45000.0, 4500.0, 0.0, 25)

println("[T5 JULIA] Modules AO5, AP5, AQ5, AR5 trained successfully.")
