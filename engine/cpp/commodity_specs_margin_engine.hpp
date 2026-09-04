#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Commodity Specs & Margin.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) CommoditySpecsMarginState {
    double account_equity;           // 8 bytes
    double total_initial_margin;     // 8 bytes
    double total_maint_margin;       // 8 bytes
    double margin_excess;            // 8 bytes
    double margin_proximity_score;   // 8 bytes
    double leverage_utilization_pct; // 8 bytes
    uint32_t is_margin_safe;         // 4 bytes
    uint32_t is_margin_call;         // 4 bytes
    uint8_t padding[8];              // 8 bytes (total = 64 bytes)
};

static_assert(sizeof(CommoditySpecsMarginState) == 64, "CommodSpecsMarginState must be exactly 64 bytes");

class CommoditySpecsMarginEngine {
public:
    static void audit_margin(
        CommoditySpecsMarginState& state,
        double equity,
        double initial_m,
        double maint_m
    ) {
        state.account_equity = equity;
        state.total_initial_margin = initial_m;
        state.total_maint_margin = maint_m;
        state.margin_excess = equity - maint_m;
        state.leverage_utilization_pct = (initial_m / std::max(1.0, equity)) * 100.0;

        if (initial_m > maint_m) {
            state.margin_proximity_score = (equity - maint_m) / (initial_m - maint_m);
        } else {
            state.margin_proximity_score = 1.0;
        }

        state.is_margin_safe = (state.margin_proximity_score >= 1.0) ? 1 : 0;
        state.is_margin_call = (equity < maint_m) ? 1 : 0;
    }
};

} // namespace optionalpha
