#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for 10-Archetype Institutional Iron Condor (Bisette & Van Der Post).
 * sizeof(InstitutionalIronCondorState) == 64 bytes.
 */
struct alignas(64) InstitutionalIronCondorState {
    double expected_price_gbm;     // 8 bytes
    double net_premium_credit;      // 8 bytes
    double max_risk_capital;        // 8 bytes
    double portfolio_delta;         // 8 bytes
    double portfolio_gamma;         // 8 bytes
    double portfolio_theta;         // 8 bytes
    uint32_t archetype_id;          // 4 bytes (1..10)
    uint16_t dte;                   // 2 bytes
    uint8_t is_iv_crush_target;     // 1 byte
    uint8_t is_martingale_valid;    // 1 byte
    uint8_t padding[8];             // 8 bytes (Total = 64 bytes)
};

static_assert(sizeof(InstitutionalIronCondorState) == 64, "InstitutionalIronCondorState must be exactly 64 bytes");

class InstitutionalIronCondorEngine {
public:
    static void configure_archetype(
        InstitutionalIronCondorState& state,
        uint32_t archetype_id,
        double spot,
        double drift,
        double sigma,
        double time_years
    ) {
        state.archetype_id = archetype_id;
        state.expected_price_gbm = spot * std::exp(drift * time_years);
        state.is_martingale_valid = (std::abs(state.expected_price_gbm - spot) < 1.0) ? 1 : 0;
        state.is_iv_crush_target = (archetype_id == 2) ? 1 : 0;
    }
};

} // namespace optionalpha
