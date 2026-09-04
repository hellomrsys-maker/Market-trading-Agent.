// engine/cpp/put_hot_path.hpp
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

class PutHotPathEngine {
public:
    static inline double compute_put_payoff(double spot, double strike, double premium, double multiplier = 100.0) {
        return (std::max(0.0, strike - spot) - premium) * multiplier;
    }

    static inline bool evaluate_put_risk_gate(ZeroBridgeStateVector* state, double required_collateral_dollars, double max_allowed_collateral = 100000.0) {
        if (!state) return false;
        double current_equity = state->equity.load(std::memory_order_relaxed);
        if (required_collateral_dollars > current_equity * 0.90) {
            return false; // Cash collateral exceeds 90% of account equity
        }
        if (state->is_halted()) {
            return false; // Circuit breaker active
        }
        return true;
    }
};

} // namespace optionalpha
