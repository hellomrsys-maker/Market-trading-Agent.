# Phase 9 Training Matrix Runner (T5 - Julia)
# Benchmarks Modules AG5, AH5, AI5, AJ5

include("vix_term_structure_engine.jl")
include("dynamic_gamma_scalping_engine.jl")
include("volatility_edge_expiration_engine.jl")
include("statistical_mean_reversion_engine.jl")

using .VixTermStructureEngine
using .DynamicGammaScalpingEngine
using .VolatilityEdgeExpirationEngine
using .StatisticalMeanReversionEngine

println("[T5 JULIA] Starting Quantitative Volatility & Mean Reversion Simulation for Phase 9...")

# 1. Train AG5
vix_res = analyze_vix_curve(13.80, 14.50, 15.60, 30)

# 2. Train AH5
band_res = compute_band(0.05, 0.005, 1.0)

# 3. Train AI5
pin_res = calculate_pinning(100.20, 100.0, 0.5, 12000)

# 4. Train AJ5
z_res = evaluate_zscore(2.15, 0.0, 1.0)

println("[T5 JULIA] Modules AG5, AH5, AI5, AJ5 trained successfully.")
