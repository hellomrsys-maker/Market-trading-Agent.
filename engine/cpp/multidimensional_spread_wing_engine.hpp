#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Multi-Dimensional Spreads & Wings.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) MultidimensionalSpreadWingState {
    float long_strike_k1;           // 4 bytes
    float short_strike_k2;          // 4 bytes
    float upper_strike_k3;          // 4 bytes
    float net_cash_flow;            // 4 bytes
    float max_profit_potential;     // 4 bytes
    float max_loss_risk;            // 4 bytes
    float upside_breakeven;         // 4 bytes
    float downside_breakeven;       // 4 bytes
    float butterfly_escape_strike;  // 4 bytes
    uint32_t spread_archetype_id;   // 4 bytes (0: Ratio, 1: Backspread, 2: Diagonal, 3: Fly, 4: Condor)
    uint32_t is_credit_spread;      // 4 bytes
    uint32_t escape_viable_flag;    // 4 bytes
    uint8_t padding[16];            // 16 bytes padding -> Total 64 bytes
};

static_assert(sizeof(MultidimensionalSpreadWingState) == 64, "MultidimensionalSpreadWingState must be exactly 64 bytes for Zero-Bridge synchronization");

class MultidimensionalSpreadWingEngine {
public:
    static void structure_ratio_spread(
        MultidimensionalSpreadWingState& state,
        float k1, float k2, float prem_long, float prem_short
    ) {
        state.long_strike_k1 = k1;
        state.short_strike_k2 = k2;
        state.net_cash_flow = (2.0f * prem_short) - prem_long;
        float strike_diff = k2 - k1;
        state.max_profit_potential = strike_diff + state.net_cash_flow;
        state.upside_breakeven = k2 + state.max_profit_potential;
        state.butterfly_escape_strike = k2 + strike_diff;

        state.spread_archetype_id = 0; // Ratio
        state.is_credit_spread = state.net_cash_flow >= 0.0f ? 1 : 0;
        state.escape_viable_flag = 1;
    }
};

} // namespace optionalpha
