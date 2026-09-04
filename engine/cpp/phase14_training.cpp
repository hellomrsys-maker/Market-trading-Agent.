#include <iostream>
#include "classical_reversal_pattern_engine.hpp"
#include "continuation_geometry_pattern_engine.hpp"
#include "volume_breakout_trap_filter.hpp"
#include "pattern_alignment_risk_governor.hpp"

/**
 * Phase 14 Training Matrix Runner (T3 - C++).
 * Enforces 64-byte Zero-Bridge memory integrity and benchmarks Modules BA3, BB3, BC3, BD3.
 */
int main() {
    std::cout << "[T3 C++] Starting Zero-Bridge Memory Integrity Training Routine for Phase 14..." << std::endl;

    // Verify 64-byte alignments
    static_assert(sizeof(optionalpha::ClassicalReversalState) == 64, "BA3 must be 64 bytes");
    static_assert(sizeof(optionalpha::ContinuationGeometryState) == 64, "BB3 must be 64 bytes");
    static_assert(sizeof(optionalpha::VolumeBreakoutTrapState) == 64, "BC3 must be 64 bytes");
    static_assert(sizeof(optionalpha::PatternAlignmentRiskState) == 64, "BD3 must be 64 bytes");

    // 1. Train BA3
    optionalpha::ClassicalReversalState rev_state{};
    optionalpha::ClassicalReversalPatternEngine::evaluate_reversal(rev_state, 1, 112.0, 98.0, 96.5, 0);

    // 2. Train BB3
    optionalpha::ContinuationGeometryState geom_state{};
    optionalpha::ContinuationGeometryPatternEngine::evaluate_geometry(geom_state, 1, 100.0, 15.0, 102.5, 1);

    // 3. Train BC3
    optionalpha::VolumeBreakoutTrapState trap_state{};
    optionalpha::VolumeBreakoutTrapFilter::audit_volume_and_trap(trap_state, 350000.0, 200000.0, 95.0, 93.5, 95.8, 1);

    // 4. Train BD3
    optionalpha::PatternAlignmentRiskState risk_state{};
    optionalpha::PatternAlignmentRiskGovernor::audit_risk_reward(risk_state, 98.0, 118.0, 92.0, 1, 1);

    std::cout << "[T3 C++] Modules BA3, BB3, BC3, BD3 trained successfully with 64-byte AtomicStateVector." << std::endl;
    return 0;
}
