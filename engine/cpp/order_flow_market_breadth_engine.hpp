#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Order Flow & Market Breadth (Bob Lang).
 * sizeof(OrderFlowMarketBreadthState) == 64 bytes.
 */
struct alignas(64) OrderFlowMarketBreadthState {
    double mcclellan_oscillator;       // 8 bytes
    double mcclellan_summation;        // 8 bytes
    double arms_trin_ratio;            // 8 bytes
    double chaikin_money_flow;         // 8 bytes
    double option_order_flow_vol;      // 8 bytes
    double flow_normal_ratio;          // 8 bytes
    uint32_t is_unusual_flow_detected; // 4 bytes
    uint32_t is_tko_breakout;          // 4 bytes
    uint32_t is_trin_extreme_fear;     // 4 bytes
    uint8_t padding[4];                // 4 bytes (Total = 64 bytes)
};

static_assert(sizeof(OrderFlowMarketBreadthState) == 64, "OrderFlowMarketBreadthState must be exactly 64 bytes");

class OrderFlowMarketBreadthEngine {
public:
    static void audit_market_breadth(
        OrderFlowMarketBreadthState& state,
        double daily_vol,
        double avg_vol,
        double adv_issues,
        double dec_issues,
        double adv_vol,
        double dec_vol
    ) {
        state.option_order_flow_vol = daily_vol;
        state.flow_normal_ratio = daily_vol / std::max(1.0, avg_vol);
        state.is_unusual_flow_detected = (state.flow_normal_ratio >= 5.0) ? 1 : 0;

        double ad_ratio = adv_issues / std::max(1.0, dec_issues);
        double vol_ratio = adv_vol / std::max(1.0, dec_vol);
        state.arms_trin_ratio = ad_ratio / std::max(0.001, vol_ratio);
        state.is_trin_extreme_fear = (state.arms_trin_ratio >= 1.50) ? 1 : 0;
    }
};

} // namespace optionalpha
