// engine/cpp/tri_state_hot_path.hpp
// OptionAlpha Agent — C++20 Sub-Microsecond Tri-State Evaluation on 64-Byte AtomicStateVector
// Polyglot Pillar 4: C++20 Engine Core & Zero-Bridge

#pragma once

#include "zero_bridge.hpp"
#include <cstdint>
#include <string>
#include <algorithm>

namespace optionalpha {

enum class CppActionType : uint8_t {
    BUY = 0,
    SELL = 1,
    HOLD = 2
};

struct CppTriStateResult {
    CppActionType action;
    const char* strategy_target;
    double confidence;
    bool risk_approved;
    int32_t contract_multiplier;
};

class TriStateHotPathEngine {
public:
    static inline CppTriStateResult evaluate_fast(
        const ZeroBridgeStateVector* state,
        double spot,
        double current_vix,
        double daily_pnl_cents,
        double vrp,
        double iv_rank,
        int32_t active_positions,
        double daily_loss_limit_cents = 200000.0, // $2,000 in cents
        int32_t max_positions = 6
    ) {
        // 1. Check Circuit Breaker Flags from 64-Byte AtomicStateVector
        if (state && state->is_halted()) {
            return { CppActionType::HOLD, "CIRCUIT_BREAKER_HALT", 1.0, false, 100 };
        }

        // 2. VIX Breaker
        if (current_vix >= 35.0) {
            return { CppActionType::HOLD, "CASH_PRESERVATION", 1.0, false, 100 };
        }

        // 3. Daily Loss Limit
        if (daily_pnl_cents <= -std::abs(daily_loss_limit_cents)) {
            return { CppActionType::HOLD, "DAILY_LOSS_LOCKOUT", 1.0, false, 100 };
        }

        // 4. Capacity Limit
        if (active_positions >= max_positions) {
            return { CppActionType::HOLD, "PORTFOLIO_CAPACITY_CAP", 0.85, false, 100 };
        }

        // 5. Positive Variance Risk Premium Edge (SELL)
        if (vrp > 0.03 && iv_rank >= 30.0) {
            double conf = std::min(0.95, 0.60 + vrp * 4.0);
            return { CppActionType::SELL, "WHEEL_CSP", conf, true, 100 };
        }

        // Default Equilibrium
        return { CppActionType::HOLD, "AWAIT_OPTIMAL_DISLOCATION", 0.60, true, 100 };
    }
};

} // namespace optionalpha
