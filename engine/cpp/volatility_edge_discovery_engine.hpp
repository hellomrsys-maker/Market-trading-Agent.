#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Volatility Edge Discovery.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) VolatilityEdgeDiscoveryState {
    double iv_30d;                   // 8 bytes
    double hv_30d;                   // 8 bytes
    double vol_spread;               // 8 bytes
    double iv_rank_pct;              // 8 bytes
    uint32_t is_expensive_edge;      // 4 bytes
    uint32_t is_cheap_edge;          // 4 bytes
    uint32_t edge_regime_flag;       // 4 bytes (1 Short Vol, 2 Long Vol, 0 Neutral)
    uint8_t padding[20];             // 20 bytes (total = 64 bytes)
};

static_assert(sizeof(VolatilityEdgeDiscoveryState) == 64, "VolatilityEdgeDiscoveryState must be exactly 64 bytes");

class VolatilityEdgeDiscoveryEngine {
public:
    static void evaluate_edge(
        VolatilityEdgeDiscoveryState& state,
        double iv,
        double hv,
        double min_iv,
        double max_iv
    ) {
        state.iv_30d = iv;
        state.hv_30d = hv;
        state.vol_spread = iv - hv;

        double rng = std::max(1.0, max_iv - min_iv);
        state.iv_rank_pct = std::max(0.0, std::min(100.0, ((iv - min_iv) / rng) * 100.0));

        state.is_expensive_edge = (state.vol_spread >= 4.0 || state.iv_rank_pct >= 75.0) ? 1 : 0;
        state.is_cheap_edge = (state.vol_spread <= -2.0 || state.iv_rank_pct <= 25.0) ? 1 : 0;

        if (state.is_expensive_edge) state.edge_regime_flag = 1;
        else if (state.is_cheap_edge) state.edge_regime_flag = 2;
        else state.edge_regime_flag = 0;
    }
};

} // namespace optionalpha
