#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Volatility Edge & Expiration Microstructure.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) VolatilityEdgeState {
    double spot_price;               // 8 bytes
    double target_pin_strike;        // 8 bytes
    double dte_days;                 // 8 bytes
    double pinning_gravitational_score; // 8 bytes
    double portfolio_vega;           // 8 bytes
    double portfolio_theta;          // 8 bytes
    double vega_theta_ratio;         // 8 bytes
    uint32_t is_pinning_candidate;   // 4 bytes
    uint32_t risk_budget_balanced;   // 4 bytes (total = 64 bytes)
};

static_assert(sizeof(VolatilityEdgeState) == 64, "VolatilityEdgeState must be exactly 64 bytes");

class VolatilityEdgeExpirationEngine {
public:
    static void evaluate_expiration_edge(
        VolatilityEdgeState& state,
        double spot,
        double strike,
        double dte,
        int32_t open_interest,
        double vega,
        double theta
    ) {
        state.spot_price = spot;
        state.target_pin_strike = strike;
        state.dte_days = dte;
        
        double dist = std::abs(spot - strike);
        double t_factor = std::exp(-std::max(0.01, dte) * 2.0);
        state.pinning_gravitational_score = (open_interest / ((dist * dist) + 1.0)) * t_factor;
        state.is_pinning_candidate = (dist < 2.0 && dte <= 1.0 && open_interest > 5000) ? 1 : 0;

        state.portfolio_vega = vega;
        state.portfolio_theta = theta;
        double abs_t = std::max(1e-4, std::abs(theta));
        state.vega_theta_ratio = std::abs(vega) / abs_t;
        state.risk_budget_balanced = (state.vega_theta_ratio <= 3.5) ? 1 : 0;
    }
};

} // namespace optionalpha
