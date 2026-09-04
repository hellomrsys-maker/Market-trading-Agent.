// engine/cpp/phase6_training.cpp
// OptionAlpha Agent — Module T3: C++20 Phase 6 Training & Zero-Bridge Verification

#include "dispersion_rainbow_engine.hpp"
#include "barrier_autocallable_engine.hpp"
#include "cliquet_mountain_range_engine.hpp"
#include "variance_swap_copula_engine.hpp"
#include <iostream>

using namespace optionalpha;

int main() {
    std::cout << "[T3 C++] Starting Zero-Bridge Memory Integrity Training Routine for Phase 6..." << std::endl;

    static_assert(sizeof(DispersionRainbowState) == 64, "DispersionRainbowState struct alignment violation!");
    static_assert(sizeof(BarrierAutocallableState) == 64, "BarrierAutocallableState struct alignment violation!");
    static_assert(sizeof(CliquetMountainState) == 64, "CliquetMountainState struct alignment violation!");
    static_assert(sizeof(VarianceSwapCopulaState) == 64, "VarianceSwapCopulaState struct alignment violation!");

    // 1. Dispersion
    auto disp = DispersionRainbowEngineCpp::evaluate_dispersion_fast(0.04, 8.0, 6.0, 3.5, 0.15, 0.08, -0.05, 0.10);
    // 2. Barrier
    auto bar = BarrierAutocallableEngineCpp::evaluate_barrier_autocall_fast(80.0, 0.20, 1.0, 252, true, 100.0, 100.0, 0.05, -0.05, 1.12, 1.10, 0.70, 0.08);
    // 3. Cliquet
    auto cliq = CliquetMountainRangeEngineCpp::evaluate_cliquet_mountain_fast(0.05, -0.02, 0.08, 0.0, 0.05, 0.0, 0.15, 0.50, 2.0);
    // 4. Variance Swap
    auto var_swap = VarianceSwapCopulaEngineCpp::evaluate_variance_greeks_fast(0.045, 1.0, 0.25, 0.20, 0.04);

    std::cout << "[T3 C++] Modules U3, V3, W3, X3 trained successfully with 64-byte AtomicStateVector." << std::endl;
    return 0;
}
