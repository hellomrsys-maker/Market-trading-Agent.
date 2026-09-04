#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Wheel Strategy Lifecycle.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) WheelStrategyState {
    double spot_price;               // 8 bytes
    double shares_cost_basis;        // 8 bytes
    double total_accumulated_income; // 8 bytes
    double true_net_cost_basis;      // 8 bytes
    double active_strike_price;      // 8 bytes
    double profit_captured_pct;      // 8 bytes
    uint32_t current_wheel_state;    // 4 bytes (1 Cash, 2 Short Put, 3 Stock Assigned, 4 Covered Call)
    uint32_t is_50pct_profit_hit;    // 4 bytes (1 True, 0 False)
    uint8_t padding[8];              // 8 bytes (total = 64 bytes)
};

static_assert(sizeof(WheelStrategyState) == 64, "WheelStrategyState must be exactly 64 bytes");

class WheelStrategyEngine {
public:
    static void track_lifecycle(
        WheelStrategyState& state,
        uint32_t state_id,
        double spot,
        double cost_basis,
        double put_prem,
        double call_prem,
        double dividends,
        double strike,
        double orig_prem,
        double curr_prem
    ) {
        state.spot_price = spot;
        state.shares_cost_basis = cost_basis;
        state.total_accumulated_income = put_prem + call_prem + dividends;
        state.true_net_cost_basis = cost_basis - state.total_accumulated_income;
        state.active_strike_price = strike;
        state.current_wheel_state = state_id;

        double profit_captured = orig_prem - curr_prem;
        state.profit_captured_pct = (orig_prem > 0.0) ? (profit_captured / orig_prem) * 100.0 : 0.0;
        state.is_50pct_profit_hit = (state.profit_captured_pct >= 50.0) ? 1 : 0;
    }
};

} // namespace optionalpha
