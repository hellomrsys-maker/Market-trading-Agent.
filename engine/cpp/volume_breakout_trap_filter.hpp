#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Volume Breakout & Trap Filters.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) VolumeBreakoutTrapState {
    double breakout_volume;          // 8 bytes
    double sma20_volume;             // 8 bytes
    double volume_surge_ratio;       // 8 bytes
    double key_structural_level;     // 8 bytes
    double closing_price;            // 8 bytes
    uint32_t is_volume_confirmed;    // 4 bytes
    uint32_t is_wyckoff_trap;        // 4 bytes
    uint32_t trap_type_id;           // 4 bytes (1 Spring, 2 Upthrust, 0 None)
    uint8_t padding[12];             // 12 bytes (total = 64 bytes)
};

static_assert(sizeof(VolumeBreakoutTrapState) == 64, "VolumeBreakoutTrapState must be exactly 64 bytes");

class VolumeBreakoutTrapFilter {
public:
    static void audit_volume_and_trap(
        VolumeBreakoutTrapState& state,
        double vol,
        double sma_vol,
        double key_level,
        double extreme_px,
        double close_px,
        uint32_t is_support
    ) {
        state.breakout_volume = vol;
        state.sma20_volume = sma_vol;
        state.volume_surge_ratio = vol / std::max(1.0, sma_vol);
        state.is_volume_confirmed = (state.volume_surge_ratio >= 1.50) ? 1 : 0;

        state.key_structural_level = key_level;
        state.closing_price = close_px;

        if (is_support == 1) {
            state.is_wyckoff_trap = (extreme_px < key_level && close_px >= key_level) ? 1 : 0;
            state.trap_type_id = state.is_wyckoff_trap ? 1 : 0;
        } else {
            state.is_wyckoff_trap = (extreme_px > key_level && close_px <= key_level) ? 1 : 0;
            state.trap_type_id = state.is_wyckoff_trap ? 2 : 0;
        }
    }
};

} // namespace optionalpha
