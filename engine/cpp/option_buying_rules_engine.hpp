// engine/cpp/option_buying_rules_engine.hpp
// OptionAlpha Agent — Module J3: C++20 Option Buyer's Zero-Bridge Hot-Path
#pragma once

#include "zero_bridge.hpp"
#include <cmath>

namespace optionalpha {

struct alignas(64) OptionBuyerState {
    double entry_price;
    double current_stop_loss;
    double target_1;
    double target_2;
    int holding_days;
    bool is_active_position;
    char milestone_status[18]; // e.g., "TRAIL_AT_COST"
    char pad[6];              // 64-byte alignment
};

class OptionBuyingRulesEngineCpp {
public:
    static inline OptionBuyerState update_stop(
        double entry_cost,
        double current_price,
        double t1,
        double t2,
        double initial_sl,
        int holding_days
    ) {
        OptionBuyerState state{};
        state.entry_price = entry_cost;
        state.target_1 = t1;
        state.target_2 = t2;
        state.holding_days = holding_days;
        state.is_active_position = holding_days <= 3;

        if (current_price >= t2) {
            state.current_stop_loss = t1;
        } else if (current_price >= t1) {
            state.current_stop_loss = entry_cost;
        } else {
            state.current_stop_loss = initial_sl;
        }

        return state;
    }
};

} // namespace optionalpha
