#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Mean Reversion & Squeeze Core (Nishant Pant).
 * sizeof(MeanReversionSqueezeState) == 64 bytes.
 */
struct alignas(64) MeanReversionSqueezeState {
    double pnr_threshold;        // 8 bytes
    double bollinger_upper;       // 8 bytes
    double bollinger_lower;       // 8 bytes
    double keltner_upper;         // 8 bytes
    double keltner_lower;         // 8 bytes
    double current_adx;           // 8 bytes
    float current_rsi;            // 4 bytes
    float current_atr;            // 4 bytes
    uint16_t dte;                 // 2 bytes
    uint8_t is_squeeze_active;    // 1 byte
    uint8_t is_pnr_breached;      // 1 byte
    uint8_t dmi_bullish_cross;    // 1 byte
    uint8_t dmi_bearish_cross;    // 1 byte
    uint8_t cut_50pct_loss;       // 1 byte
    uint8_t padding[1];           // 1 byte (Total = 64 bytes)
};

static_assert(sizeof(MeanReversionSqueezeState) == 64, "MeanReversionSqueezeState must be exactly 64 bytes");

class MeanReversionSqueezeEngine {
public:
    static void compute_pnr(
        MeanReversionSqueezeState& state,
        double long_strike,
        double short_strike,
        uint16_t dte,
        float atr,
        double current_price
    ) {
        state.dte = dte;
        state.current_atr = atr;
        double pnr_offset = (long_strike * dte * atr) / 2000.0;
        state.pnr_threshold = long_strike - pnr_offset;
        state.is_pnr_breached = (current_price < state.pnr_threshold) ? 1 : 0;
        state.cut_50pct_loss = (state.is_pnr_breached && (dte < 15)) ? 1 : 0;
    }
};

} // namespace optionalpha
