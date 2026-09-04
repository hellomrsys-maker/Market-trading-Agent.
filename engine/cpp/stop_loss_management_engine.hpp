// engine/cpp/stop_loss_management_engine.hpp
// OptionAlpha Agent — Module K3: C++20 Zero-Bridge Hard Stop Loss Execution
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) StopLossState {
    double percentage_sl;
    double structural_sl;
    double volatility_sl;
    double rr_2to1_sl;
    double active_hard_sl;
    bool is_breached;
    char stop_type[16]; // e.g. "VOLATILITY_STOP"
};

class StopLossManagementEngineCpp {
public:
    static inline StopLossState compute_active_sl(
        double entry,
        double target,
        double support,
        double atr,
        double current_price,
        bool is_long
    ) {
        double pct_sl = is_long ? entry * 0.98 : entry * 1.02;
        double sr_sl = is_long ? support - 0.5 : support + 0.5;
        double vol_sl = is_long ? entry - (atr * 1.5) : entry + (atr * 1.5);
        double rr_sl = is_long ? entry - (std::abs(target - entry) / 2.0) : entry + (std::abs(target - entry) / 2.0);

        // Active hard stop is the tightest defensive structural stop
        double hard_sl = is_long ? std::max({pct_sl, sr_sl, vol_sl, rr_sl}) : std::min({pct_sl, sr_sl, vol_sl, rr_sl});
        bool breached = is_long ? (current_price <= hard_sl) : (current_price >= hard_sl);

        StopLossState state{};
        state.percentage_sl = pct_sl;
        state.structural_sl = sr_sl;
        state.volatility_sl = vol_sl;
        state.rr_2to1_sl = rr_sl;
        state.active_hard_sl = hard_sl;
        state.is_breached = breached;
        return state;
    }
};

} // namespace optionalpha
