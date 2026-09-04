#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Schwager Price Action & Traps.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) SchwagerPriceActionState {
    double current_high;             // 8 bytes
    double current_low;              // 8 bytes
    double current_close;            // 8 bytes
    double stop_level;               // 8 bytes
    double projected_target;         // 8 bytes
    uint32_t key_reversal_flag;      // 4 bytes (+1 Bull, -1 Bear, 0 None)
    uint32_t trap_flag;              // 4 bytes (+1 Spring, -1 Upthrust, 0 None)
    uint32_t gap_type;               // 4 bytes (1 Breakaway, 2 Runaway, 3 Exhaustion)
    uint32_t volume_confirmed;       // 4 bytes (1 True, 0 False)
    uint8_t padding[8];              // 8 bytes (total = 64 bytes)
};

static_assert(sizeof(SchwagerPriceActionState) == 64, "SchwagerPriceActionState must be exactly 64 bytes");

class SchwagerPriceActionEngine {
public:
    static void evaluate_bar(
        SchwagerPriceActionState& state,
        double prev_low, double prev_high, double prev_close,
        double curr_low, double curr_high, double curr_close,
        double curr_vol, double avg_vol,
        double support, double resistance
    ) {
        state.current_high = curr_high;
        state.current_low = curr_low;
        state.current_close = curr_close;

        bool vol_surge = (avg_vol <= 0.0) || (curr_vol >= avg_vol * 1.3);
        state.volume_confirmed = vol_surge ? 1 : 0;

        // Key Reversals
        if (curr_low < prev_low && curr_close > prev_close && vol_surge) {
            state.key_reversal_flag = 1;
            state.stop_level = curr_low;
        } else if (curr_high > prev_high && curr_close < prev_close && vol_surge) {
            state.key_reversal_flag = 2; // Bearish
            state.stop_level = curr_high;
        } else {
            state.key_reversal_flag = 0;
            state.stop_level = 0.0;
        }

        // Traps
        if (curr_low < support && curr_close >= support) {
            state.trap_flag = 1; // Spring
        } else if (curr_high > resistance && curr_close <= resistance) {
            state.trap_flag = 2; // Upthrust
        } else {
            state.trap_flag = 0;
        }

        state.projected_target = curr_close * 1.05;
        state.gap_type = 0;
    }
};

} // namespace optionalpha
