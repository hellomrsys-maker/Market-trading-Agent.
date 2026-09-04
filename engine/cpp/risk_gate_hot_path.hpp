// engine/cpp/risk_gate_hot_path.hpp
// OptionAlpha Agent — C++20 Zero-Bridge 64-Byte AtomicStateVector Circuit Breaker Hot Path
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <cstdint>
#include <cmath>

namespace optionalpha {

class RiskGateHotPathEngine {
public:
    static inline bool is_order_permitted(
        const ZeroBridgeStateVector* state,
        int64_t order_collateral_cents,
        double incoming_delta_dollars,
        int32_t active_positions,
        double current_vix,
        int64_t max_loss_limit_cents = 200000, // $2,000 in cents
        double max_portfolio_delta_dollars = 50000.0,
        int32_t max_positions = 6,
        double max_vix = 35.0
    ) {
        if (!state) return false;

        // 1. Bitmask Breaker Check
        if (state->is_halted()) {
            return false;
        }

        // 2. Daily Loss Limit Check
        int64_t daily_pnl = state->daily_pnl.load(std::memory_order_relaxed);
        if (daily_pnl <= -std::abs(max_loss_limit_cents)) {
            return false;
        }

        // 3. VIX Hard Circuit Breaker
        if (current_vix >= max_vix) {
            return false;
        }

        // 4. Maximum Position Count
        if (active_positions >= max_positions) {
            return false;
        }

        // 5. Portfolio Delta Bounding
        double current_delta = state->net_delta.load(std::memory_order_relaxed);
        if (std::abs(current_delta + incoming_delta_dollars) > max_portfolio_delta_dollars) {
            return false;
        }

        // 6. Single Position Size Cap (Max 20% Equity)
        int64_t equity = state->equity.load(std::memory_order_relaxed);
        if (order_collateral_cents > equity * 0.20) {
            return false;
        }

        return true;
    }
};

} // namespace optionalpha
