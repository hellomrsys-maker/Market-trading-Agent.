#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Higher-Order Greeks & Volatility Surface.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) SecondOrderGreeksSurfaceState {
    float delta;                    // 4 bytes
    float gamma;                    // 4 bytes
    float vega;                     // 4 bytes
    float theta;                    // 4 bytes
    float rho;                      // 4 bytes
    float vanna;                    // 4 bytes
    float vomma;                    // 4 bytes
    float charm;                    // 4 bytes
    float forward_implied_vol;      // 4 bytes
    float term_structure_slope;     // 4 bytes
    uint32_t term_structure_regime; // 4 bytes (0: Flat, 1: Contango, 2: Backwardation)
    uint32_t is_atm_flag;           // 4 bytes
    uint8_t padding[16];            // 16 bytes padding -> Total 64 bytes
};

static_assert(sizeof(SecondOrderGreeksSurfaceState) == 64, "SecondOrderGreeksSurfaceState must be exactly 64 bytes for Zero-Bridge synchronization");

class SecondOrderGreeksSurfaceEngine {
public:
    static float calculate_forward_vol(float vol1, int days1, float vol2, int days2) {
        if (days2 <= days1) return vol2;
        float v1_sq_t = (vol1 * vol1) * static_cast<float>(days1);
        float v2_sq_t = (vol2 * vol2) * static_cast<float>(days2);
        float dt = static_cast<float>(days2 - days1);
        float num = v2_sq_t - v1_sq_t;
        return num > 0.0f ? std::sqrt(num / dt) : 0.0f;
    }
};

} // namespace optionalpha
