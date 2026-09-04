# Phase 15 Training Matrix Runner (T5 - Julia)
# Benchmarks Modules BE5, BF5, BG5, BH5.

include("all_weather_vomma_engine.jl")
include("gamma_scalping_stochastic_engine.jl")
include("bladerunner_carry_forex_engine.jl")
include("structured_collar_box_arbitrage_engine.jl")

using .AllWeatherVommaEngine
using .GammaScalpingStochasticEngine
using .BladerunnerCarryForexEngine
using .StructuredCollarBoxArbitrageEngine

function run_phase15_training()
    println("[T5 JULIA] Starting Quantitative Math Simulation for Phase 15...")

    # 1. Train BE5
    margin_res = audit_margin(-7800.0, -11000.0, -1000.0, 20000.0)
    
    # 2. Train BF5
    scalp_res = evaluate_scalping(12.5, 0.04, 0.15, 0.02, 0.05)

    # 3. Train BG5
    carry_res = calculate_carry(4.50, 0.10, 100000.0)

    # 4. Train BH5
    collar_res = structure_collar(79.0, 88.0, 1.75, 85.0, 1.24)
    box_res = evaluate_box(95.0, 105.0, 8.80)

    println("[T5 JULIA] Modules BE5, BF5, BG5, BH5 trained successfully.")
end

run_phase15_training()
