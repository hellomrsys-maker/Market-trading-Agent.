#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Bladerunner Forex & Carry Trade.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) BladerunnerCarryState {
    double spot_price;               // 8 bytes
    double ema_20_level;             // 8 bytes
    double daily_carry_interest;     // 8 bytes
    double optimal_kelly_allocation; // 8 bytes
    uint32_t polarity_is_above_ema;  // 4 bytes (1 Long, 0 Short)
    uint32_t trade_signal_action;    // 4 bytes (1 Buy, 2 Sell, 0 Wait)
    uint32_t is_positive_carry;      // 4 bytes
    uint8_t padding[20];             // 20 bytes (total = 64 bytes)
};

static_assert(sizeof(BladerunnerCarryState) == 64, "BladerunnerCarryState must be exactly 64 bytes");

class BladerunnerCarryForexEngine {
public:
    static void evaluate_forex_system(
        BladerunnerCarryState& state,
        double spot,
        double ema20,
        uint32_t rejected,
        uint32_t confirmed,
        double rate_long,
        double rate_short,
        double units,
        double win_prob,
        double win_loss
    ) {
        state.spot_price = spot;
        state.ema_20_level = ema20;
        state.polarity_is_above_ema = (spot > ema20) ? 1 : 0;

        if (state.polarity_is_above_ema && rejected && confirmed) state.trade_signal_action = 1; // Buy
        else if (!state.polarity_is_above_ema && rejected && confirmed) state.trade_signal_action = 2; // Sell
        else state.trade_signal_action = 0; // Wait

        double diff = (rate_long - rate_short) / 100.0;
        state.daily_carry_interest = (diff * units) / 365.0;
        state.is_positive_carry = (state.daily_carry_interest > 0.0) ? 1 : 0;

        double w = std::max(0.01, std::min(0.99, win_prob));
        double r = std::max(0.01, win_loss);
        double k = w - ((1.0 - w) / r);
        state.optimal_kelly_allocation = std::max(0.0, std::min(0.25, k));
    }
};

} // namespace optionalpha
