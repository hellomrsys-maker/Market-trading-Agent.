#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Delivery Roll Governor.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) DeliveryRollState {
    double front_month_volume;       // 8 bytes
    double next_month_volume;        // 8 bytes
    int32_t days_to_fnd;             // 4 bytes
    int32_t days_to_ltd;             // 4 bytes
    uint32_t is_physical_delivery;   // 4 bytes
    uint32_t is_volume_crossover;    // 4 bytes
    uint32_t is_fnd_danger;          // 4 bytes
    uint32_t roll_directive_action;  // 4 bytes (0 Hold, 1 Roll, 2 Liquidate)
    uint8_t padding[24];             // 24 bytes (total = 64 bytes)
};

static_assert(sizeof(DeliveryRollState) == 64, "DeliveryRollState must be exactly 64 bytes");

class DeliveryRollGovernorEngine {
public:
    static void evaluate_roll(
        DeliveryRollState& state,
        uint32_t is_physical,
        int32_t days_fnd,
        int32_t days_ltd,
        double vol_m1,
        double vol_m2
    ) {
        state.is_physical_delivery = is_physical;
        state.days_to_fnd = days_fnd;
        state.days_to_ltd = days_ltd;
        state.front_month_volume = vol_m1;
        state.next_month_volume = vol_m2;

        state.is_volume_crossover = (vol_m2 > vol_m1) ? 1 : 0;
        state.is_fnd_danger = (is_physical && days_fnd <= 5) ? 1 : 0;

        if (is_physical && days_fnd <= 1) {
            state.roll_directive_action = 2; // Liquidate
        } else if (state.is_fnd_danger || state.is_volume_crossover) {
            state.roll_directive_action = 1; // Roll
        } else {
            state.roll_directive_action = 0; // Hold
        }
    }
};

} // namespace optionalpha
