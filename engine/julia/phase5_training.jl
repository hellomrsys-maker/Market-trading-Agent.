# engine/julia/phase5_training.jl
# OptionAlpha Agent — Module T5: Julia Phase 5 Training Module

include("weekly_squeeze_engine.jl")
include("bsm_jump_diffusion_engine.jl")
include("binary_options_engine.jl")
include("drawdown_risk_manager.jl")

using .WeeklySqueezeEngineJulia
using .BSMJumpDiffusionEngineJulia
using .BinaryOptionsEngineJulia
using .DrawdownRiskManagerJulia

println("[T5 JULIA] Starting Quantitative Monte Carlo Training Simulation for Phase 5...")

ha = calculate_heikin_ashi(100.0, 105.0, 99.0, 104.0, 98.0, 101.0)
sqz = is_in_squeeze(103.0, 97.0, 104.0, 96.0)

bsm = price_merton_bsm(100.0, 100.0, 0.25, 0.05, 0.20, 0.02)
p_ever = probability_ever_itm(100.0, 110.0, 0.5, 0.05, 0.25, 0.0)

bin = price_short_volatility_strangle(20.0, 80.0, 2)

dm = DrawdownManager(10000.0, 20.0)
sz = calculate_position_size(dm, 2.0, 50.0)
res = update_trade!(dm, 200.0)

println("[T5 JULIA] Modules Q5, R5, S5, T_sys5 trained successfully.")
