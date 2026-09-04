// engine/cpp/cfi_valuation_breadth_engine.hpp
// OptionAlpha Agent — Module O3: C++20 Institutional Valuation & TRIN Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>

namespace optionalpha {

struct alignas(64) CFIValuationBreadthState {
    double ben_graham_intrinsic_value;
    double trin_index;
    double adx_trend_strength;
    bool is_golden_cross;
    bool is_breadth_extreme;
    char regime_status[18]; // "TRIN_OVERSOLD"
    char pad[6];            // 64-byte alignment
};

class CFIValuationBreadthEngineCpp {
public:
    static inline CFIValuationBreadthState compute_valuation_fast(
        double eps,
        double bvps,
        double trin,
        double adx,
        bool golden_cross
    ) {
        double graham = (eps > 0.0 && bvps > 0.0) ? std::sqrt(22.5 * eps * bvps) : 0.0;

        CFIValuationBreadthState state{};
        state.ben_graham_intrinsic_value = graham;
        state.trin_index = trin;
        state.adx_trend_strength = adx;
        state.is_golden_cross = golden_cross;
        state.is_breadth_extreme = (trin < 0.50 || trin > 3.00);
        return state;
    }
};

} // namespace optionalpha
