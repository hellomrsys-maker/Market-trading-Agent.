#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Statistical Mean Reversion.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) StatisticalMeanReversionState {
    double current_spread_value;     // 8 bytes
    double rolling_mean;             // 8 bytes
    double rolling_std;              // 8 bytes
    double zscore;                   // 8 bytes
    double ou_theta;                 // 8 bytes
    double ou_half_life;             // 8 bytes
    double hurst_exponent;           // 8 bytes
    int32_t signal_action;           // 4 bytes (+1 Buy, -1 Sell, 0 Neutral, 99 Stop)
    uint32_t regime_mean_reverting;  // 4 bytes (1 = True, 0 = False) (total = 64 bytes)
};

static_assert(sizeof(StatisticalMeanReversionState) == 64, "StatisticalMeanReversionState must be exactly 64 bytes");

class StatisticalMeanReversionEngine {
public:
    static void evaluate_signals(
        StatisticalMeanReversionState& state,
        double current_val,
        double mean,
        double std_dev,
        double theta,
        double hurst
    ) {
        state.current_spread_value = current_val;
        state.rolling_mean = mean;
        state.rolling_std = std_dev;

        double s = std::max(1e-5, std_dev);
        state.zscore = (current_val - mean) / s;

        state.ou_theta = theta;
        state.ou_half_life = (theta > 0) ? (std::log(2.0) / theta) : 9999.0;
        state.hurst_exponent = hurst;
        state.regime_mean_reverting = (hurst < 0.45) ? 1 : 0;

        if (state.zscore >= 3.5 || state.zscore <= -3.5) {
            state.signal_action = 99; // Stop
        } else if (state.zscore >= 2.0) {
            state.signal_action = -1; // Short spread
        } else if (state.zscore <= -2.0) {
            state.signal_action = 1;  // Long spread
        } else if (std::abs(state.zscore) <= 0.5) {
            state.signal_action = 0;  // Exit
        }
    }
};

} // namespace optionalpha
