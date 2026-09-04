#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Volatility Skew Arbitrage & BWB.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) VolatilitySkewState {
    double strike_skew_slope;        // 8 bytes
    double term_structure_slope;     // 8 bytes
    double bwb_net_credit;           // 8 bytes
    double bwb_max_profit;           // 8 bytes
    uint32_t is_steep_put_skew;      // 4 bytes
    uint32_t is_contango_term;       // 4 bytes
    uint32_t has_zero_downside_risk; // 4 bytes
    uint32_t optimal_structure_id;   // 4 bytes (1 BWB / Ratio, 2 Call Backspread, 0 Condor/Vertical)
    uint8_t padding[16];             // 16 bytes (total = 64 bytes)
};

static_assert(sizeof(VolatilitySkewState) == 64, "VolatilitySkewState must be exactly 64 bytes");

class VolatilitySkewArbitrageEngine {
public:
    static void evaluate_skew(
        VolatilitySkewState& state,
        double iv_atm,
        double iv_put25,
        double iv_call25,
        double iv_30,
        double iv_90,
        double bwb_c1,
        double bwb_c2,
        double bwb_c3,
        double k1,
        double k2
    ) {
        state.strike_skew_slope = (iv_put25 - iv_call25) / std::max(1e-4, iv_atm);
        state.term_structure_slope = (iv_90 - iv_30) / std::max(1e-4, iv_30);

        state.is_steep_put_skew = (state.strike_skew_slope >= 0.25) ? 1 : 0;
        state.is_contango_term = (state.term_structure_slope > 0.05) ? 1 : 0;

        if (state.is_steep_put_skew) state.optimal_structure_id = 1;
        else if (state.strike_skew_slope < 0.05) state.optimal_structure_id = 2;
        else state.optimal_structure_id = 0;

        state.bwb_net_credit = (2.0 * bwb_c2) - bwb_c1 - bwb_c3;
        state.bwb_max_profit = (k2 - k1) + state.bwb_net_credit;
        state.has_zero_downside_risk = (state.bwb_net_credit >= 0.0) ? 1 : 0;
    }
};

} // namespace optionalpha
