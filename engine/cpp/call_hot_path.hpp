// engine/cpp/call_hot_path.hpp
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

class CallHotPathEngine {
public:
    static inline double compute_call_payoff(double spot, double strike, double premium, double multiplier = 100.0) {
        return (std::max(0.0, spot - strike) - premium) * multiplier;
    }

    static inline bool evaluate_call_risk_gate(ZeroBridgeStateVector* state, double contract_delta_dollars, double max_allowed_delta = 50000.0) {
        if (!state) return false;
        double current_delta = state->net_delta.load(std::memory_order_relaxed);
        if (std::abs(current_delta + contract_delta_dollars) > max_allowed_delta) {
            return false; // Exceeds portfolio delta limit
        }
        if (state->is_halted()) {
            return false; // Circuit breaker active
        }
        return true;
    }
};

} // namespace optionalpha
