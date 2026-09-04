#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for COT Sentiment & Open Interest.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) CotSentimentState {
    double current_net_position;     // 8 bytes
    double min_net_3yr;              // 8 bytes
    double max_net_3yr;              // 8 bytes
    double cot_index_pct;            // 8 bytes
    double price_change;             // 8 bytes
    double open_interest_change;     // 8 bytes
    uint32_t institutional_bias;     // 4 bytes (1 Strong Bull, 2 Weak Bull, 3 Strong Bear, 4 Weak Bear)
    uint32_t is_extreme_signal;      // 4 bytes (1 True, 0 False)
    uint8_t padding[8];              // 8 bytes (total = 64 bytes)
};

static_assert(sizeof(CotSentimentState) == 64, "CotSentimentState must be exactly 64 bytes");

class CotInstitutionalSentimentEngine {
public:
    static void evaluate_cot(
        CotSentimentState& state,
        double current_net, double min_net, double max_net,
        double p_change, double oi_change
    ) {
        state.current_net_position = current_net;
        state.min_net_3yr = min_net;
        state.max_net_3yr = max_net;
        state.price_change = p_change;
        state.open_interest_change = oi_change;

        double rng = std::max(1.0, max_net - min_net);
        double idx = ((current_net - min_net) / rng) * 100.0;
        state.cot_index_pct = std::max(0.0, std::min(100.0, idx));
        state.is_extreme_signal = (state.cot_index_pct >= 90.0 || state.cot_index_pct <= 10.0) ? 1 : 0;

        if (p_change > 0 && oi_change > 0) state.institutional_bias = 1;
        else if (p_change > 0 && oi_change <= 0) state.institutional_bias = 2;
        else if (p_change < 0 && oi_change > 0) state.institutional_bias = 3;
        else state.institutional_bias = 4;
    }
};

} // namespace optionalpha
