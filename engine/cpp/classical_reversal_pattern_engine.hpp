#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Classical Reversal Patterns.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) ClassicalReversalState {
    double pattern_neckline;         // 8 bytes
    double pattern_height;           // 8 bytes
    double measured_price_target;    // 8 bytes
    double current_spot_price;       // 8 bytes
    uint32_t pattern_type_id;        // 4 bytes (1 Head&Shoulders, 2 Double Top, 3 Double Bottom)
    uint32_t is_structure_valid;     // 4 bytes
    uint32_t is_breakout_confirmed;  // 4 bytes
    uint8_t padding[20];             // 20 bytes (total = 64 bytes)
};

static_assert(sizeof(ClassicalReversalState) == 64, "ClassicalReversalState must be exactly 64 bytes");

class ClassicalReversalPatternEngine {
public:
    static void evaluate_reversal(
        ClassicalReversalState& state,
        uint32_t type_id,
        double head_or_peak,
        double neckline,
        double spot,
        uint32_t is_bullish
    ) {
        state.pattern_type_id = type_id;
        state.pattern_neckline = neckline;
        state.current_spot_price = spot;
        state.pattern_height = std::abs(head_or_peak - neckline);

        if (is_bullish == 1) {
            state.measured_price_target = neckline + state.pattern_height;
            state.is_breakout_confirmed = (spot > neckline) ? 1 : 0;
        } else {
            state.measured_price_target = neckline - state.pattern_height;
            state.is_breakout_confirmed = (spot < neckline) ? 1 : 0;
        }

        state.is_structure_valid = 1;
    }
};

} // namespace optionalpha
