#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Fundamental Stock Repair & Volatility Routing (Brown & Jaffee).
 * sizeof(FundamentalStockRepairState) == 64 bytes.
 */
struct alignas(64) FundamentalStockRepairState {
    double pe_ratio;                 // 8 bytes
    double peg_ratio;                // 8 bytes
    double debt_to_assets_ratio;     // 8 bytes
    double repair_long_strike;       // 8 bytes
    double repair_short_strike;      // 8 bytes
    double cash_reserve_pct;         // 8 bytes
    uint32_t sec_material_flag;       // 4 bytes
    uint32_t use_naked_over_spread;  // 4 bytes
    uint32_t is_repair_recommended;  // 4 bytes
    uint8_t padding[4];              // 4 bytes (Total = 64 bytes)
};

static_assert(sizeof(FundamentalStockRepairState) == 64, "FundamentalStockRepairState must be exactly 64 bytes");

class FundamentalStockRepairEngine {
public:
    static void evaluate_repair(
        FundamentalStockRepairState& state,
        double price,
        double cost_basis,
        double vix,
        double cash_pct
    ) {
        state.cash_reserve_pct = cash_pct;
        state.use_naked_over_spread = (vix >= 20.0) ? 1 : 0;
        double drop_pct = ((cost_basis - price) / cost_basis) * 100.0;
        if (drop_pct >= 15.0 && drop_pct <= 25.0) {
            state.is_repair_recommended = 1;
            state.repair_long_strike = price;
            state.repair_short_strike = price + ((cost_basis - price) / 2.0);
        } else {
            state.is_repair_recommended = 0;
        }
    }
};

} // namespace optionalpha
