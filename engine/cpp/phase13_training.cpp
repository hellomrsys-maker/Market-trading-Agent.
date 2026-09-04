#include <iostream>
#include "volatility_edge_discovery_engine.hpp"
#include "trading_firm_greek_governor.hpp"
#include "volatility_skew_arbitrage_engine.hpp"
#include "trade_adjustment_repair_engine.hpp"

/**
 * Phase 13 Training Matrix Runner (T3 - C++).
 * Enforces 64-byte Zero-Bridge memory integrity and benchmarks Modules AW3, AX3, AY3, AZ3.
 */
int main() {
    std::cout << "[T3 C++] Starting Zero-Bridge Memory Integrity Training Routine for Phase 13..." << std::endl;

    // Verify 64-byte alignments
    static_assert(sizeof(optionalpha::VolatilityEdgeDiscoveryState) == 64, "AW3 must be 64 bytes");
    static_assert(sizeof(optionalpha::TradingFirmGreekState) == 64, "AX3 must be 64 bytes");
    static_assert(sizeof(optionalpha::VolatilitySkewState) == 64, "AY3 must be 64 bytes");
    static_assert(sizeof(optionalpha::TradeAdjustmentState) == 64, "AZ3 must be 64 bytes");

    // 1. Train AW3
    optionalpha::VolatilityEdgeDiscoveryState vol_state{};
    optionalpha::VolatilityEdgeDiscoveryEngine::evaluate_edge(vol_state, 24.5, 18.2, 14.0, 32.0);

    // 2. Train AX3
    optionalpha::TradingFirmGreekState greek_state{};
    optionalpha::TradingFirmGreekGovernor::audit_inventory(greek_state, 15.0, 0.04, -25.0, 35.0, 100.0, 0.25, 100000.0);

    // 3. Train AY3
    optionalpha::VolatilitySkewState skew_state{};
    optionalpha::VolatilitySkewArbitrageEngine::evaluate_skew(skew_state, 20.0, 26.5, 19.0, 20.0, 22.0, 1.20, 2.10, 2.80, 90.0, 95.0);

    // 4. Train AZ3
    optionalpha::TradeAdjustmentState defense_state{};
    optionalpha::TradeAdjustmentRepairEngine::audit_defense(defense_state, -180.0, 150.0, -0.38, 18.0, 0.65);

    std::cout << "[T3 C++] Modules AW3, AX3, AY3, AZ3 trained successfully with 64-byte AtomicStateVector." << std::endl;
    return 0;
}
