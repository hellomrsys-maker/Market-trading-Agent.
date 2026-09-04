#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Covered Calls (CC).
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) CoveredCallYieldState {
    double stock_cost_basis;         // 8 bytes
    double current_spot;             // 8 bytes
    double strike_price;             // 8 bytes
    double call_premium;             // 8 bytes
    double breakeven_price;          // 8 bytes
    double annualized_static_yield;  // 8 bytes
    double annualized_max_yield;     // 8 bytes
    uint32_t early_assignment_risk;  // 4 bytes
    uint8_t padding[4];              // 4 bytes (total = 64 bytes)
};

static_assert(sizeof(CoveredCallYieldState) == 64, "CoveredCallYieldState must be exactly 64 bytes");

class CoveredCallYieldEngine {
public:
    static void evaluate_covered_call(
        CoveredCallYieldState& state,
        double basis,
        double spot,
        double strike,
        double premium,
        double dte,
        double dividend
    ) {
        state.stock_cost_basis = basis;
        state.current_spot = spot;
        state.strike_price = strike;
        state.call_premium = premium;
        state.breakeven_price = basis - premium;

        double static_yield = ((premium + dividend) / basis) * 100.0;
        state.annualized_static_yield = static_yield * (365.0 / std::max(1.0, dte));

        double cap_gain = std::max(0.0, strike - basis);
        double max_yield = ((cap_gain + premium + dividend) / basis) * 100.0;
        state.annualized_max_yield = max_yield * (365.0 / std::max(1.0, dte));

        double intrinsic = std::max(0.0, spot - strike);
        double extrinsic = std::max(0.0, premium - intrinsic);
        state.early_assignment_risk = (spot > strike && extrinsic < dividend) ? 1 : 0;
    }
};

} // namespace optionalpha
