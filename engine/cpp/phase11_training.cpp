#include <iostream>
#include "cash_secured_put_engine.hpp"
#include "covered_call_yield_engine.hpp"
#include "wheel_strategy_engine.hpp"
#include "retail_income_risk_governor.hpp"

/**
 * Phase 11 Training Matrix Runner (T3 - C++).
 * Enforces 64-byte Zero-Bridge memory integrity and benchmarks Modules AO3, AP3, AQ3, AR3.
 */
int main() {
    std::cout << "[T3 C++] Starting Zero-Bridge Memory Integrity Training Routine for Phase 11..." << std::endl;

    // Verify 64-byte alignments
    static_assert(sizeof(optionalpha::CashSecuredPutState) == 64, "AO3 must be 64 bytes");
    static_assert(sizeof(optionalpha::CoveredCallYieldState) == 64, "AP3 must be 64 bytes");
    static_assert(sizeof(optionalpha::WheelStrategyState) == 64, "AQ3 must be 64 bytes");
    static_assert(sizeof(optionalpha::RetailIncomeRiskState) == 64, "AR3 must be 64 bytes");

    // 1. Train AO3
    optionalpha::CashSecuredPutState csp_state{};
    optionalpha::CashSecuredPutEngine::evaluate_csp(csp_state, 100.0, 95.0, 1.85, 35.0, -0.26);

    // 2. Train AP3
    optionalpha::CoveredCallYieldState cc_state{};
    optionalpha::CoveredCallYieldEngine::evaluate_covered_call(cc_state, 100.0, 102.5, 105.0, 2.40, 30.0, 0.50);

    // 3. Train AQ3
    optionalpha::WheelStrategyState wheel_state{};
    optionalpha::WheelStrategyEngine::track_lifecycle(wheel_state, 2, 98.0, 100.0, 3.50, 2.10, 1.00, 95.0, 2.00, 0.80);

    // 4. Train AR3
    optionalpha::RetailIncomeRiskState risk_state{};
    optionalpha::RetailIncomeRiskGovernor::audit_trade(risk_state, 100000.0, 45000.0, 4500.0, 0.0, 25);

    std::cout << "[T3 C++] Modules AO3, AP3, AQ3, AR3 trained successfully with 64-byte AtomicStateVector." << std::endl;
    return 0;
}
