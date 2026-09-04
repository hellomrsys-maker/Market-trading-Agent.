// engine/cpp/binary_options_engine.hpp
// OptionAlpha Agent — Module S3: C++20 Binary Options & Volatility Strangle Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) BinaryOptionsState {
    double total_collateral;
    double max_profit;
    double max_loss;
    double reward_risk_ratio;
    double cutoff_loss_trigger;
    bool is_long_volatility;
    char strategy_tag[19]; // e.g. "SHORT_STRANGLE_PREM"
    char pad[4];           // 64-byte alignment
};

class BinaryOptionsEngineCpp {
public:
    static inline BinaryOptionsState evaluate_short_strangle_fast(
        double high_ask, double low_bid, int contracts, double risk_multiple = 3.0
    ) {
        double long_cost = low_bid;
        double short_collateral = 100.0 - high_ask;
        double total_collateral = (long_cost + short_collateral) * contracts;
        double max_profit = (200.0 * contracts) - total_collateral;

        double upper_loss = short_collateral - (100.0 - long_cost);
        double lower_loss = long_cost - (100.0 - short_collateral);
        double max_loss = std::max(std::abs(upper_loss), std::abs(lower_loss)) * contracts;

        BinaryOptionsState state{};
        state.total_collateral = total_collateral;
        state.max_profit = max_profit;
        state.max_loss = max_loss;
        state.reward_risk_ratio = max_profit / std::max(1e-4, max_loss);
        state.cutoff_loss_trigger = max_profit * risk_multiple;
        state.is_long_volatility = false;
        return state;
    }
};

} // namespace optionalpha
