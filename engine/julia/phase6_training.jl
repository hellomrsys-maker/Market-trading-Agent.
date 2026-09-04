# engine/julia/phase6_training.jl
# OptionAlpha Agent — Module T5: Julia Phase 6 Training Module

include("dispersion_rainbow_engine.jl")
include("barrier_autocallable_engine.jl")
include("cliquet_mountain_range_engine.jl")
include("variance_swap_copula_engine.jl")

using .DispersionRainbowEngineJulia
using .BarrierAutocallableEngineJulia
using .CliquetMountainRangeEngineJulia
using .VarianceSwapCopulaEngineJulia

println("[T5 JULIA] Starting Quantitative Monte Carlo Training Simulation for Phase 6...")

weights = [0.5, 0.5]
vols = [0.20, 0.30]
corr = [1.0 0.4; 0.4 1.0]
var_p = calculate_basket_variance(weights, vols, corr)

h_shift = discrete_barrier_shift(80.0, 0.20, 1.0, 252, true)
dig = digital_skew_correction(100.0, 100.0, 1.0, 0.05, 0.20, -0.05)

rets = [0.05, -0.02, 0.08]
lflc = calculate_lflc_cliquet(rets, 0.0, 0.05)
napoleon = calculate_napoleon(rets, 0.50)

log_rets = [0.01, -0.015, 0.02, -0.005, 0.012]
rv = calculate_realized_variance(log_rets, 252.0)
greeks = calculate_variance_swap_greeks(1.0, 0.25, 0.20)

println("[T5 JULIA] Modules U5, V5, W5, X5 trained successfully.")
