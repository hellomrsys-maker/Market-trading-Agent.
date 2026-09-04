# Phase 14 Training Matrix Runner (T5 - Julia)
# Benchmarks Modules BA5, BB5, BC5, BD5

include("classical_reversal_pattern_engine.jl")
include("continuation_geometry_pattern_engine.jl")
include("volume_breakout_trap_filter.jl")
include("pattern_alignment_risk_governor.jl")

using .ClassicalReversalPatternEngine
using .ContinuationGeometryPatternEngine
using .VolumeBreakoutTrapFilter
using .PatternAlignmentRiskGovernor

println("[T5 JULIA] Starting Classical Chart Pattern & Geometry Simulation for Phase 14...")

# 1. Train BA5
rev_res = evaluate_head_and_shoulders(105.0, 112.0, 104.5, 98.0, 96.5, false)

# 2. Train BB5
geom_res = evaluate_triangle(0.0, 0.12, 15.0, 100.0, 102.5)

# 3. Train BC5
trap_res = evaluate_volume(350000.0, 200000.0, true)

# 4. Train BD5
risk_res = audit_risk_reward(98.0, 118.0, 92.0, 1, 1)

println("[T5 JULIA] Modules BA5, BB5, BC5, BD5 trained successfully.")
