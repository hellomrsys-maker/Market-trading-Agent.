// engine/cpp/wheel_hot_path.hpp
// OptionAlpha Agent — C++20 Hot-Path Wheel Strategy Risk & Collateral Gate
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <cstdint>
#include <algorithm>

namespace optionalpha {

class WheelHotPathEngine {
public:
    // Sub-microsecond Wheel CSP collateral check
    static inline bool validate_csp_collateral(
        const ZeroBridgeStateVector* state,
        double strike,
        int32_t qty = 1,
        double max_equity_allocation_pct = 0.50
    ) {
        if (!state) return false;
        double current_equity = state->equity.load(std::memory_order_relaxed);
        double required_collateral = strike * 100.0 * qty;
        
        if (required_collateral > current_equity * max_equity_allocation_pct) {
            return false; // Cash collateral exceeds risk limit
        }
        if (state->is_halted()) {
            return false;
        }
        return true;
    }

    // Sub-microsecond Covered Call strike validator (Strike >= Cost Basis)
    static inline bool validate_covered_call_strike(double strike, double cost_basis) {
        return strike >= cost_basis;
    }
};

} // namespace optionalpha
