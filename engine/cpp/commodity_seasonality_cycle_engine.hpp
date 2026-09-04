#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Commodity Seasonality.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) CommoditySeasonalityState {
    double base_seasonal_score;      // 8 bytes
    double weather_shock_severity;   // 8 bytes
    double adjusted_seasonal_score;  // 8 bytes
    double old_crop_price;           // 8 bytes
    double new_crop_price;           // 8 bytes
    double crop_spread_value;        // 8 bytes
    uint32_t is_inverted_market;     // 4 bytes
    uint32_t seasonal_regime;        // 4 bytes (1 Bull, -1 Bear, 0 Neutral)
    uint8_t padding[8];              // 8 bytes (total = 64 bytes)
};

static_assert(sizeof(CommoditySeasonalityState) == 64, "CommoditySeasonalityState must be exactly 64 bytes");

class CommoditySeasonalityCycleEngine {
public:
    static void evaluate_seasonality(
        CommoditySeasonalityState& state,
        double base_score,
        double weather_severity,
        double old_crop,
        double new_crop
    ) {
        state.base_seasonal_score = base_score;
        state.weather_shock_severity = weather_severity;
        
        double adj = std::max(-1.0, std::min(1.0, base_score + (weather_severity * 0.5)));
        state.adjusted_seasonal_score = adj;

        state.old_crop_price = old_crop;
        state.new_crop_price = new_crop;
        state.crop_spread_value = old_crop - new_crop;
        state.is_inverted_market = (state.crop_spread_value > 0.0) ? 1 : 0;

        if (adj >= 0.5) state.seasonal_regime = 1;
        else if (adj <= -0.5) state.seasonal_regime = 2; // Bear
        else state.seasonal_regime = 0;
    }
};

} // namespace optionalpha
