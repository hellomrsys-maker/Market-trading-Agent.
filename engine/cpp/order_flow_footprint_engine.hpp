// engine/cpp/order_flow_footprint_engine.hpp
// OptionAlpha Agent — Module I3: C++20 Order Flow Footprint & VPOC Delta Hot-Path
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) FootprintOrderFlowState {
    double bar_delta;
    double cumulative_delta;
    double vpoc_price;
    double vah_price;
    double val_price;
    bool is_delta_divergence;
    char dominant_flow[15]; // "AGGRESSIVE_BUY" / "AGGRESSIVE_SEL"
    char pad[9];            // 64-byte alignment
};

class OrderFlowFootprintEngineCpp {
public:
    static inline FootprintOrderFlowState compute_footprint_fast(
        double total_ask_vol,
        double total_bid_vol,
        double current_cum_delta,
        double vpoc,
        double vah,
        double val,
        bool price_rising
    ) {
        double delta = total_ask_vol - total_bid_vol;
        double new_cum_delta = current_cum_delta + delta;
        bool divergence = (price_rising && delta < 0.0) || (!price_rising && delta > 0.0);

        FootprintOrderFlowState state{};
        state.bar_delta = delta;
        state.cumulative_delta = new_cum_delta;
        state.vpoc_price = vpoc;
        state.vah_price = vah;
        state.val_price = val;
        state.is_delta_divergence = divergence;
        return state;
    }
};

} // namespace optionalpha
