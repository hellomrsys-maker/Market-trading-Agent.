#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for VIX Term Structure & Volatility Arbitrage.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) VixTermStructureState {
    double spot_vix;                 // 8 bytes
    double m1_futures_price;         // 8 bytes
    double m2_futures_price;         // 8 bytes
    double term_slope;               // 8 bytes
    double annualized_roll_yield;    // 8 bytes
    double vvix_index;               // 8 bytes
    uint32_t contango_flag;          // 4 bytes (1 = Contango, 0 = Backwardation)
    uint32_t tail_risk_spike_flag;   // 4 bytes (1 = Spike Alert, 0 = Normal)
    uint8_t padding[8];              // 8 bytes (total = 64 bytes)
};

static_assert(sizeof(VixTermStructureState) == 64, "VixTermStructureState must be exactly 64 bytes");

class VixTermStructureEngine {
public:
    static void update_vix_state(
        VixTermStructureState& state,
        double spot_vix,
        double m1,
        double m2,
        double vvix,
        int delta_days
    ) {
        state.spot_vix = spot_vix;
        state.m1_futures_price = m1;
        state.m2_futures_price = m2;
        state.term_slope = m2 - m1;
        
        int d = std::max(1, delta_days);
        state.annualized_roll_yield = ((m2 - m1) / m1) * (365.0 / d) * 100.0;
        state.vvix_index = vvix;
        state.contango_flag = (state.term_slope > 0.15) ? 1 : 0;
        state.tail_risk_spike_flag = (vvix >= 115.0) ? 1 : 0;
    }
};

} // namespace optionalpha
