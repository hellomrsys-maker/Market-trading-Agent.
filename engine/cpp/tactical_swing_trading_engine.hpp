#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Tactical Swing Trading.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) TacticalSwingState {
    float point_a_price;            // 4 bytes
    float point_b_price;            // 4 bytes
    float point_c_price;            // 4 bytes
    float point_d_target;           // 4 bytes
    float swing_stop_loss;          // 4 bytes
    float reward_to_risk_ratio;     // 4 bytes
    float ema10;                    // 4 bytes
    float ema21;                    // 4 bytes
    float sma50;                    // 4 bytes
    float sma200;                   // 4 bytes
    uint32_t pattern_type;          // 4 bytes (0: None, 1: Bullish ABCD, 2: Bearish ABCD, 3: Bull Flag, 4: Bear Flag)
    uint32_t is_golden_cross;       // 4 bytes
    uint32_t is_death_cross;        // 4 bytes
    uint8_t padding[12];            // 12 bytes padding -> Total 64 bytes
};

static_assert(sizeof(TacticalSwingState) == 64, "TacticalSwingState must be exactly 64 bytes for Zero-Bridge synchronization");

class TacticalSwingTradingEngine {
public:
    static void evaluate_abcd(
        TacticalSwingState& state,
        float a, float b, float c, bool is_bullish
    ) {
        state.point_a_price = a;
        state.point_b_price = b;
        state.point_c_price = c;
        float ab_leg = std::abs(a - b);

        if (is_bullish) {
            state.point_d_target = c + ab_leg;
            state.swing_stop_loss = c * 0.98f;
            state.pattern_type = 1; // Bullish ABCD
            float risk = c - state.swing_stop_loss;
            state.reward_to_risk_ratio = risk > 0.0f ? (state.point_d_target - c) / risk : 0.0f;
        } else {
            state.point_d_target = c - ab_leg;
            state.swing_stop_loss = c * 1.02f;
            state.pattern_type = 2; // Bearish ABCD
            float risk = state.swing_stop_loss - c;
            state.reward_to_risk_ratio = risk > 0.0f ? (c - state.point_d_target) / risk : 0.0f;
        }
    }
};

} // namespace optionalpha
