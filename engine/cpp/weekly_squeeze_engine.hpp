// engine/cpp/weekly_squeeze_engine.hpp
// OptionAlpha Agent — Module Q3: C++20 Weekly Squeeze & Heikin Ashi Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) WeeklySqueezeState {
    double ha_open;
    double ha_high;
    double ha_low;
    double ha_close;
    double midpoint_entry;
    bool in_squeeze;
    bool is_strong_bull;
    bool is_strong_bear;
    char trend_tag[16]; // e.g. "BULL_STACKED"
    char pad[5];        // 64-byte alignment
};

class WeeklySqueezeEngineCpp {
public:
    static inline WeeklySqueezeState evaluate_squeeze_fast(
        double o, double h, double l, double c,
        double prev_ha_o, double prev_ha_c,
        double bb_u, double bb_l,
        double kc_u, double kc_l,
        double ema13, double ema21, double ema55
    ) {
        WeeklySqueezeState state{};
        state.ha_open = (prev_ha_o + prev_ha_c) / 2.0;
        state.ha_close = (o + h + l + c) / 4.0;
        state.ha_high = std::max({h, state.ha_open, state.ha_close});
        state.ha_low = std::min({l, state.ha_open, state.ha_close});

        state.is_strong_bull = (state.ha_close > state.ha_open) && (std::abs(state.ha_low - state.ha_open) < 1e-4);
        state.is_strong_bear = (state.ha_close < state.ha_open) && (std::abs(state.ha_high - state.ha_open) < 1e-4);
        state.in_squeeze = (bb_u < kc_u) && (bb_l > kc_l);
        state.midpoint_entry = (o + c) / 2.0;

        return state;
    }
};

} // namespace optionalpha
