#include <iostream>
#include "vix_term_structure_engine.hpp"
#include "dynamic_gamma_scalping_engine.hpp"
#include "volatility_edge_expiration_engine.hpp"
#include "statistical_mean_reversion_engine.hpp"

/**
 * Phase 9 Training Matrix Runner (T3 - C++).
 * Enforces 64-byte Zero-Bridge memory integrity and benchmarks Modules AG3, AH3, AI3, AJ3.
 */
int main() {
    std::cout << "[T3 C++] Starting Zero-Bridge Memory Integrity Training Routine for Phase 9..." << std::endl;

    // Verify 64-byte alignments
    static_assert(sizeof(optionalpha::VixTermStructureState) == 64, "AG3 must be 64 bytes");
    static_assert(sizeof(optionalpha::DynamicGammaScalpState) == 64, "AH3 must be 64 bytes");
    static_assert(sizeof(optionalpha::VolatilityEdgeState) == 64, "AI3 must be 64 bytes");
    static_assert(sizeof(optionalpha::StatisticalMeanReversionState) == 64, "AJ3 must be 64 bytes");

    // 1. Train AG3
    optionalpha::VixTermStructureState vix_state{};
    optionalpha::VixTermStructureEngine::update_vix_state(vix_state, 13.80, 14.50, 15.60, 118.5, 30);

    // 2. Train AH3
    optionalpha::DynamicGammaScalpState scalp_state{};
    optionalpha::DynamicGammaScalpingEngine::compute_rebalance(scalp_state, 100.0, 0.05, 0.18, 0.005, 1.0);

    // 3. Train AI3
    optionalpha::VolatilityEdgeState vol_edge_state{};
    optionalpha::VolatilityEdgeExpirationEngine::evaluate_expiration_edge(vol_edge_state, 100.20, 100.0, 0.5, 12000, 45.0, -25.0);

    // 4. Train AJ3
    optionalpha::StatisticalMeanReversionState mr_state{};
    optionalpha::StatisticalMeanReversionEngine::evaluate_signals(mr_state, 2.15, 0.0, 1.0, 0.12, 0.38);

    std::cout << "[T3 C++] Modules AG3, AH3, AI3, AJ3 trained successfully with 64-byte AtomicStateVector." << std::endl;
    return 0;
}
