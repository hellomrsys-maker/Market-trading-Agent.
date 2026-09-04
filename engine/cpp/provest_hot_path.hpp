// engine/cpp/provest_hot_path.hpp
// OptionAlpha Agent — C++20 Zero-Bridge Hot-Path PROVEST Volatility Decile & Strategy Resolver
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <algorithm>
#include <vector>
#include <cmath>

namespace optionalpha {

class PROVESTHotPathEngine {
public:
    static inline int32_t compute_fast_decile(const double* sorted_iv_history, int32_t count, double current_iv) {
        if (!sorted_iv_history || count <= 0) return 5;
        auto it = std::upper_bound(sorted_iv_history, sorted_iv_history + count, current_iv);
        int32_t num_below = std::distance(sorted_iv_history, it);
        double percentile = static_cast<double>(num_below) / count;
        int32_t decile = static_cast<int32_t>(std::ceil(percentile * 10.0));
        return std::clamp(decile, 1, 10);
    }

    static inline const char* resolve_strategy(int32_t rel_vol_rank, int32_t directional_bias_code) {
        // directional_bias_code: 1 = Bullish, -1 = Bearish, 0 = Neutral
        if (directional_bias_code == 1) {
            return rel_vol_rank <= 4 ? "LONG_CALL_DEEP_ITM" : "BULL_PUT_SPREAD";
        } else if (directional_bias_code == -1) {
            return rel_vol_rank <= 4 ? "LONG_PUT_DEEP_ITM" : "PUT_RATIO_SPREAD_1X2";
        } else {
            if (rel_vol_rank <= 3) return "CALENDAR_SPREAD";
            if (rel_vol_rank >= 7) return "IRON_CONDOR";
            return "WHEEL_CSP";
        }
    }
};

} // namespace optionalpha
