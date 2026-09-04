# Phase 7 Training Matrix Runner (T5 - Julia)
# Benchmarks Modules Y5, Z5, AA5, AB5

include("behavioral_psychology_engine.jl")
include("cashflow_capital_ecosystem_engine.jl")
include("tactical_swing_trading_engine.jl")
include("tactical_options_discipline_engine.jl")

using .BehavioralPsychologyEngine
using .CashflowCapitalEcosystemEngine
using .TacticalSwingTradingEngine
using .TacticalOptionsDisciplineEngine

println("[T5 JULIA] Starting Quantitative Behavioral & Swing Strategy Training Simulation for Phase 7...")

# Y5
y_res = evaluate_3p_resilience(0.2, 0.2, 0.1)

# Z5
z_eco = calculate_ecosystem(3000.0, 1200.0, 300.0, 25.0, 0.25)

# AA5
aa_abcd = evaluate_abcd(40.0, 55.0, 48.0, true)

# AB5
ab_condor = structure_iron_condor(50.0, 60.0, 90.0, 100.0, 2.0, 1.0, 2.0, 1.0)

println("[T5 JULIA] Modules Y5, Z5, AA5, AB5 trained successfully.")
