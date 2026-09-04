# Phase 8 Training Matrix Runner (T5 - Julia)
# Benchmarks Modules AC5, AD5, AE5, AF5

include("options_equivalency_engine.jl")
include("second_order_greeks_surface_engine.jl")
include("multidimensional_spread_wing_engine.jl")
include("strategic_gamma_scalping_engine.jl")

using .OptionsEquivalencyEngine
using .SecondOrderGreeksSurfaceEngine
using .MultidimensionalSpreadWingEngine
using .StrategicGammaScalpingEngine

println("[T5 JULIA] Starting Quantitative Market Maker & Gamma Scalping Training Simulation for Phase 8...")

# AC5
ac_par = evaluate_parity(66.0, 65.0, 3.45, 2.10, 0.04, 71, 0.10)

# AD5
ad_fwd = calculate_forward_vol(0.36, 30, 0.54, 90)

# AE5
ae_ratio = structure_ratio_spread(50.0, 55.0, 4.0, 2.0)

# AF5
af_rent = calculate_gamma_decay_breakeven(0.03, 0.15)

println("[T5 JULIA] Modules AC5, AD5, AE5, AF5 trained successfully.")
