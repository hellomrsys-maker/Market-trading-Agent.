#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Gamma Scalping & Second-Order Greeks.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) GammaScalpingState {
    double current_delta;            // 8 bytes
    double current_gamma;            // 8 bytes
    double current_vomma;            // 8 bytes
    double current_vanna;            // 8 bytes
    double shares_to_hedge;          // 8 bytes
    uint32_t is_rebalance_required;  // 4 bytes
    uint8_t padding[20];             // 20 bytes (total = 64 bytes)
};

static_assert(sizeof(GammaScalpingState) == 64, "GammaScalpingState must be exactly 64 bytes");

class GammaScalpingStochasticEngine {
public:
    static void evaluate_scalping(
        GammaScalpingState& state,
        double delta,
        double gamma,
        double vomma,
        double vanna,
        double threshold
    ) {
        state.current_delta = delta;
        state.current_gamma = gamma;
        state.current_vomma = vomma;
        state.current_vanna = vanna;
        state.shares_to_hedge = -delta;
        state.is_rebalance_required = (std::abs(delta) >= threshold) ? 1 : 0;
    }
};

} // namespace optionalpha
