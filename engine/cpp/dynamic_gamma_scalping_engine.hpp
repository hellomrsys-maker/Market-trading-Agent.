#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Dynamic Gamma Scalping.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) DynamicGammaScalpState {
    double spot_price;               // 8 bytes
    double portfolio_gamma;          // 8 bytes
    double current_delta;            // 8 bytes
    double optimal_band_threshold;   // 8 bytes
    double realized_variance;        // 8 bytes
    double implied_variance;         // 8 bytes
    int32_t rebalance_shares;        // 4 bytes
    uint32_t trigger_flag;           // 4 bytes (1 = Triggered, 0 = Hold)
    uint8_t padding[8];              // 8 bytes (total = 64 bytes)
};

static_assert(sizeof(DynamicGammaScalpState) == 64, "DynamicGammaScalpState must be exactly 64 bytes");

class DynamicGammaScalpingEngine {
public:
    static void compute_rebalance(
        DynamicGammaScalpState& state,
        double spot,
        double gamma,
        double current_delta,
        double tx_cost,
        double risk_aversion
    ) {
        state.spot_price = spot;
        state.portfolio_gamma = gamma;
        state.current_delta = current_delta;

        double abs_g = std::max(1e-7, std::abs(gamma));
        double term = (1.5 * tx_cost * abs_g) / std::max(1e-5, risk_aversion);
        double threshold = std::cbrt(term);
        state.optimal_band_threshold = std::max(0.02, std::min(0.25, threshold));

        if (std::abs(current_delta) >= state.optimal_band_threshold) {
            state.trigger_flag = 1;
            state.rebalance_shares = static_cast<int32_t>(-current_delta * 100.0);
        } else {
            state.trigger_flag = 0;
            state.rebalance_shares = 0;
        }
    }
};

} // namespace optionalpha
