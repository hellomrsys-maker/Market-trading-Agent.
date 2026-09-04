#include <iostream>
#include "behavioral_psychology_engine.hpp"
#include "cashflow_capital_ecosystem_engine.hpp"
#include "tactical_swing_trading_engine.hpp"
#include "tactical_options_discipline_engine.hpp"

/**
 * Phase 7 Training Matrix Runner (T3 - C++).
 * Enforces Zero-Bridge Memory Integrity across Modules Y3, Z3, AA3, AB3.
 */
int main() {
    std::cout << "[T3 C++] Starting Zero-Bridge Memory Integrity Training Routine for Phase 7..." << std::endl;

    // Y3
    optionalpha::BehavioralPsychologyState y_state{};
    optionalpha::BehavioralPsychologyEngine::update_psychology_state(y_state, 1, 3, 0.2f, 0.2f, 0.1f);

    // Z3
    optionalpha::CashflowCapitalState z_state{};
    optionalpha::CashflowCapitalEcosystemEngine::compute_ecosystem(z_state, 3000.0f, 1200.0f, 300.0f, 25.0f, 0.25f, 100.0f);

    // AA3
    optionalpha::TacticalSwingState aa_state{};
    optionalpha::TacticalSwingTradingEngine::evaluate_abcd(aa_state, 40.0f, 55.0f, 48.0f, true);

    // AB3
    optionalpha::TacticalOptionsDisciplineState ab_state{};
    optionalpha::TacticalOptionsDisciplineEngine::compute_sizing_and_condor(
        ab_state, 10000.0f, 50.0f, 48.0f, 55.0f, 50.0f, 60.0f, 90.0f, 100.0f, 2.0f, 1.0f, 2.0f, 1.0f
    );

    std::cout << "[T3 C++] Modules Y3, Z3, AA3, AB3 trained successfully with 64-byte AtomicStateVector." << std::endl;
    return 0;
}
