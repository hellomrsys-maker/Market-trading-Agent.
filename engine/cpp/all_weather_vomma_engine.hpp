#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for All-Weather Vomma & SPAN Slicing.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) AllWeatherVommaState {
    double worst_case_margin_req;   // 8 bytes
    double planned_capital;          // 8 bytes
    double margin_utilization_pct;   // 8 bytes
    double net_portfolio_vomma;      // 8 bytes
    uint32_t market_regime_id;       // 4 bytes (1 Bull, 2 Sideways, 3 Grind-Down, 4 Crash)
    uint32_t is_margin_safe;         // 4 bytes
    uint32_t has_positive_vomma;     // 4 bytes
    uint8_t padding[20];             // 20 bytes (total = 64 bytes)
};

static_assert(sizeof(AllWeatherVommaState) == 64, "AllWeatherVommaState must be exactly 64 bytes");

class AllWeatherVommaEngine {
public:
    static void audit_all_weather(
        AllWeatherVommaState& state,
        double pnl_12_down,
        double pnl_20_down,
        double pnl_10_up,
        double capital,
        double vix_spike,
        double core_vomma,
        int32_t num_teenies
    ) {
        double s12 = std::abs(std::min(0.0, pnl_12_down));
        double s20 = std::abs(std::min(0.0, pnl_20_down)) / 2.0;
        double s10 = std::abs(std::min(0.0, pnl_10_up));

        state.worst_case_margin_req = std::max(s12, std::max(s20, s10));
        state.planned_capital = capital;
        state.margin_utilization_pct = (state.worst_case_margin_req / std::max(1.0, capital)) * 100.0;
        state.is_margin_safe = (state.margin_utilization_pct <= 65.0) ? 1 : 0;

        if (vix_spike >= 35.0) state.market_regime_id = 4; // Crash
        else state.market_regime_id = 1; // Bull / Sideways

        state.net_portfolio_vomma = core_vomma + (num_teenies * 0.08);
        state.has_positive_vomma = (state.net_portfolio_vomma > 0.0) ? 1 : 0;
    }
};

} // namespace optionalpha
