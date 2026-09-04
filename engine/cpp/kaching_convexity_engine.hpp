#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Weekly Cash KaChing Engine (T.R. Lawrence).
 * sizeof(KaChingConvexityState) == 64 bytes exactly.
 */
struct alignas(64) KaChingConvexityState {
    double long_put_strike;             // 8 bytes
    double short_put_strike;            // 8 bytes
    double long_put_delta;              // 8 bytes
    double short_put_delta;             // 8 bytes
    double net_weekly_premium;          // 8 bytes
    double cumulative_cash_collected;   // 8 bytes
    uint32_t days_to_earnings;          // 4 bytes
    uint16_t roll_count;                // 2 bytes
    uint8_t double_dip_active;          // 1 byte
    uint8_t is_supersized;              // 1 byte
    uint8_t status_flags;               // 1 byte
    uint8_t padding[7];                 // 7 bytes padding -> 64 bytes
};

static_assert(sizeof(KaChingConvexityState) == 64, "KaChingConvexityState must be exactly 64 bytes!");

class KaChingConvexityEngineCpp {
public:
    static KaChingConvexityState initialize(double spot, double iv, uint32_t dte) {
        KaChingConvexityState state{};
        state.long_put_delta = (iv > 0.35) ? 0.38 : 0.25;
        state.long_put_strike = spot * (1.0 - (state.long_put_delta == 0.25 ? 0.08 : 0.05));
        state.short_put_delta = (spot >= state.long_put_strike) ? 0.50 : 0.40;
        state.short_put_strike = spot;
        state.net_weekly_premium = spot * 0.018 * (1.0 + iv);
        state.cumulative_cash_collected = state.net_weekly_premium;
        state.days_to_earnings = dte;
        state.roll_count = 0;
        state.double_dip_active = 0;
        state.is_supersized = 0;
        state.status_flags = 1;
        return state;
    }

    static void evaluate_harvest(KaChingConvexityState& state, double cur_prem, int day_of_week) {
        double banked_pct = 1.0 - (cur_prem / std::max(0.01, state.net_weekly_premium));
        if (banked_pct >= 0.80 && day_of_week <= 3) {
            state.double_dip_active = 1;
            state.cumulative_cash_collected += (state.net_weekly_premium * 0.60);
        } else if (cur_prem > 2.0 * state.net_weekly_premium && day_of_week >= 3) {
            state.roll_count++;
            state.short_put_strike -= 2.0;
            state.cumulative_cash_collected += ((state.net_weekly_premium * 1.15) - cur_prem);
        } else if (day_of_week == 5) {
            state.cumulative_cash_collected += state.net_weekly_premium;
            state.double_dip_active = 0;
        }
    }
};

} // namespace optionalpha
