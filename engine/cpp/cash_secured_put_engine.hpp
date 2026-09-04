#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Cash-Secured Puts (CSP).
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) CashSecuredPutState {
    double spot_price;               // 8 bytes
    double strike_price;             // 8 bytes
    double premium_received;         // 8 bytes
    double effective_cost_basis;     // 8 bytes
    double annualized_roc_pct;       // 8 bytes
    double put_delta;                // 8 bytes
    uint32_t pop_estimate_pct;       // 4 bytes
    uint32_t is_optimal_setup;       // 4 bytes
    uint8_t padding[8];              // 8 bytes (total = 64 bytes)
};

static_assert(sizeof(CashSecuredPutState) == 64, "CashSecuredPutState must be exactly 64 bytes");

class CashSecuredPutEngine {
public:
    static void evaluate_csp(
        CashSecuredPutState& state,
        double spot,
        double strike,
        double premium,
        double dte,
        double delta
    ) {
        state.spot_price = spot;
        state.strike_price = strike;
        state.premium_received = premium;
        state.effective_cost_basis = strike - premium;
        state.put_delta = delta;

        double collateral = strike * 100.0;
        double trade_roc = ((premium * 100.0) / collateral) * 100.0;
        state.annualized_roc_pct = trade_roc * (365.0 / std::max(1.0, dte));

        double abs_d = std::abs(delta);
        state.pop_estimate_pct = static_cast<uint32_t>((1.0 - abs_d) * 100.0);
        state.is_optimal_setup = (abs_d >= 0.20 && abs_d <= 0.30 && dte >= 30.0 && dte <= 45.0) ? 1 : 0;
    }
};

} // namespace optionalpha
