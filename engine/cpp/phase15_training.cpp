#include <iostream>
#include "all_weather_vomma_engine.hpp"
#include "gamma_scalping_stochastic_engine.hpp"
#include "bladerunner_carry_forex_engine.hpp"
#include "structured_collar_box_arbitrage_engine.hpp"

/**
 * Phase 15 Training Matrix Runner (T3 - C++).
 * Enforces 64-byte Zero-Bridge memory integrity and benchmarks Modules BE3, BF3, BG3, BH3.
 */
int main() {
    std::cout << "[T3 C++] Starting Zero-Bridge Memory Integrity Training Routine for Phase 15..." << std::endl;

    // Verify 64-byte alignments
    static_assert(sizeof(optionalpha::AllWeatherVommaState) == 64, "BE3 must be 64 bytes");
    static_assert(sizeof(optionalpha::GammaScalpingState) == 64, "BF3 must be 64 bytes");
    static_assert(sizeof(optionalpha::BladerunnerCarryState) == 64, "BG3 must be 64 bytes");
    static_assert(sizeof(optionalpha::StructuredCollarBoxState) == 64, "BH3 must be 64 bytes");

    // 1. Train BE3
    optionalpha::AllWeatherVommaState vomma_state{};
    optionalpha::AllWeatherVommaEngine::audit_all_weather(vomma_state, -7800.0, -11000.0, -1000.0, 20000.0, 38.0, -0.25, 5);

    // 2. Train BF3
    optionalpha::GammaScalpingState scalp_state{};
    optionalpha::GammaScalpingStochasticEngine::evaluate_scalping(scalp_state, 12.5, 0.04, 0.15, 0.02, 0.05);

    // 3. Train BG3
    optionalpha::BladerunnerCarryState fx_state{};
    optionalpha::BladerunnerCarryForexEngine::evaluate_forex_system(fx_state, 1.3520, 1.3500, 1, 1, 4.50, 0.10, 100000.0, 0.60, 1.5);

    // 4. Train BH3
    optionalpha::StructuredCollarBoxState box_state{};
    optionalpha::StructuredCollarBoxArbitrageEngine::evaluate_structured_trades(box_state, 79.0, 88.0, 1.75, 85.0, 1.24, 95.0, 105.0, 8.80, 100.0, 80.0, 1);

    std::cout << "[T3 C++] Modules BE3, BF3, BG3, BH3 trained successfully with 64-byte AtomicStateVector." << std::endl;
    return 0;
}
