#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Structured Collars & Long Box Arbitrage.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) StructuredCollarBoxState {
    double net_collar_premium;       // 8 bytes
    double max_upside_profit;        // 8 bytes
    double max_downside_risk;        // 8 bytes
    double box_risk_free_profit;     // 8 bytes
    double binary_net_payout;        // 8 bytes
    uint32_t is_costless_collar;     // 4 bytes
    uint32_t is_box_profitable;      // 4 bytes
    uint32_t is_binary_itm;          // 4 bytes
    uint8_t padding[12];             // 12 bytes (total = 64 bytes)
};

static_assert(sizeof(StructuredCollarBoxState) == 64, "StructuredCollarBoxState must be exactly 64 bytes");

class StructuredCollarBoxArbitrageEngine {
public:
    static void evaluate_structured_trades(
        StructuredCollarBoxState& state,
        double basis,
        double call_k,
        double call_prem,
        double put_k,
        double put_prem,
        double box_k1,
        double box_k2,
        double box_debit,
        double bet,
        double payout_pct,
        uint32_t itm
    ) {
        state.net_collar_premium = call_prem - put_prem;
        state.is_costless_collar = (state.net_collar_premium >= 0.0) ? 1 : 0;
        state.max_upside_profit = (call_k - basis) + state.net_collar_premium;
        state.max_downside_risk = (basis - put_k) - state.net_collar_premium;

        state.box_risk_free_profit = (box_k2 - box_k1) - box_debit;
        state.is_box_profitable = (state.box_risk_free_profit > 0.0) ? 1 : 0;

        state.is_binary_itm = itm;
        state.binary_net_payout = (itm == 1) ? (bet * (payout_pct / 100.0)) : (-bet * 0.90);
    }
};

} // namespace optionalpha
