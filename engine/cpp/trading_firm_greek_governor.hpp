#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Trading Firm Greek Inventory.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) TradingFirmGreekState {
    double portfolio_delta;          // 8 bytes
    double portfolio_gamma;          // 8 bytes
    double portfolio_theta;          // 8 bytes
    double portfolio_vega;           // 8 bytes
    double gamma_rent_ratio;         // 8 bytes
    double vega_pct_equity;          // 8 bytes
    uint32_t is_firm_approved;       // 4 bytes
    uint32_t is_delta_compliant;     // 4 bytes
    uint32_t is_rent_compliant;      // 4 bytes
    uint32_t is_vega_compliant;      // 4 bytes (total = 64 bytes)
};

static_assert(sizeof(TradingFirmGreekState) == 64, "TradingFirmGreekState must be exactly 64 bytes");

class TradingFirmGreekGovernor {
public:
    static void audit_inventory(
        TradingFirmGreekState& state,
        double delta,
        double gamma,
        double theta,
        double vega,
        double spot,
        double iv,
        double equity
    ) {
        state.portfolio_delta = delta;
        state.portfolio_gamma = gamma;
        state.portfolio_theta = theta;
        state.portfolio_vega = vega;

        double daily_sigma = iv / std::sqrt(252.0);
        double daily_gamma_cost = 0.5 * std::abs(gamma) * (spot * spot) * (daily_sigma * daily_sigma);
        state.gamma_rent_ratio = std::abs(theta) / std::max(1e-4, daily_gamma_cost);

        double vega_exposure = std::abs(vega) * 100.0;
        state.vega_pct_equity = (vega_exposure / std::max(1.0, equity)) * 100.0;

        state.is_delta_compliant = (std::abs(delta) <= 50.0) ? 1 : 0;
        state.is_rent_compliant = (state.gamma_rent_ratio >= 1.0) ? 1 : 0;
        state.is_vega_compliant = (state.vega_pct_equity <= 8.0) ? 1 : 0;

        state.is_firm_approved = (state.is_delta_compliant && state.is_rent_compliant && state.is_vega_compliant) ? 1 : 0;
    }
};

} // namespace optionalpha
