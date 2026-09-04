#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Continuation Geometry Patterns.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) ContinuationGeometryState {
    double breakout_price;           // 8 bytes
    double pattern_dimension_height; // 8 bytes
    double measured_price_target;    // 8 bytes
    double current_spot_price;       // 8 bytes
    uint32_t pattern_geometry_id;    // 4 bytes (1 Ascending, 2 Descending, 3 Symmetrical, 4 Flag/Pennant)
    uint32_t is_breakout_confirmed;  // 4 bytes
    uint8_t padding[24];             // 24 bytes (total = 64 bytes)
};

static_assert(sizeof(ContinuationGeometryState) == 64, "ContinuationGeometryState must be exactly 64 bytes");

class ContinuationGeometryPatternEngine {
public:
    static void evaluate_geometry(
        ContinuationGeometryState& state,
        uint32_t geom_id,
        double breakout_px,
        double dim_height,
        double spot,
        uint32_t is_bullish
    ) {
        state.pattern_geometry_id = geom_id;
        state.breakout_price = breakout_px;
        state.pattern_dimension_height = dim_height;
        state.current_spot_price = spot;

        if (is_bullish == 1) {
            state.measured_price_target = breakout_px + dim_height;
            state.is_breakout_confirmed = (spot > breakout_px) ? 1 : 0;
        } else {
            state.measured_price_target = breakout_px - dim_height;
            state.is_breakout_confirmed = (spot < breakout_px) ? 1 : 0;
        }
    }
};

} // namespace optionalpha
