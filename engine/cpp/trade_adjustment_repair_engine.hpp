#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Trade Adjustment & Repair.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) TradeAdjustmentState {
    double current_trade_pnl;        // 8 bytes
    double initial_credit_received;  // 8 bytes
    double tested_short_delta;       // 8 bytes
    double dte_days;                 // 8 bytes
    double extrinsic_remaining;      // 8 bytes
    uint32_t is_delta_breached;      // 4 bytes
    uint32_t is_max_loss_hit;        // 4 bytes
    uint32_t repair_protocol_action; // 4 bytes (0 Hold, 1 Cut Loss, 2 Roll Untested Wing, 3 Roll Time, 4 Delta Hedge)
    uint8_t padding[12];             // 12 bytes (total = 64 bytes)
};

static_assert(sizeof(TradeAdjustmentState) == 64, "TradeAdjustmentState must be exactly 64 bytes");

class TradeAdjustmentRepairEngine {
public:
    static void audit_defense(
        TradeAdjustmentState& state,
        double pnl,
        double credit,
        double short_delta,
        double dte,
        double extrinsic
    ) {
        state.current_trade_pnl = pnl;
        state.initial_credit_received = credit;
        state.tested_short_delta = short_delta;
        state.dte_days = dte;
        state.extrinsic_remaining = extrinsic;

        state.is_delta_breached = (std::abs(short_delta) >= 0.35) ? 1 : 0;
        state.is_max_loss_hit = (pnl <= -(credit * 2.0)) ? 1 : 0;

        if (state.is_max_loss_hit) {
            state.repair_protocol_action = 1; // Cut loss
        } else if (state.is_delta_breached) {
            if (dte >= 14.0 && extrinsic > 0.30) {
                state.repair_protocol_action = 2; // Roll untested wing
            } else if (dte < 7.0) {
                state.repair_protocol_action = 3; // Roll time
            } else {
                state.repair_protocol_action = 4; // Delta hedge
            }
        } else {
            state.repair_protocol_action = 0; // Hold
        }
    }
};

} // namespace optionalpha
