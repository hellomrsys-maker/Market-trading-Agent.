// engine/cpp/dealer_gamma_hot_path.hpp
// OptionAlpha Agent — C++20 Zero-Bridge Hot-Path Dealer Net Gamma & Volatility Regime Evaluator
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <cmath>

namespace optionalpha {

class DealerGammaHotPathEngine {
public:
    static inline double compute_fast_gex(
        double spot,
        const double* call_gammas,
        const double* call_ois,
        int32_t call_count,
        const double* put_gammas,
        const double* put_ois,
        int32_t put_count,
        double multiplier = 100.0
    ) {
        double call_sum = 0.0;
        for (int32_t i = 0; i < call_count; ++i) {
            call_sum += call_gammas[i] * call_ois[i];
        }

        double put_sum = 0.0;
        for (int32_t i = 0; i < put_count; ++i) {
            put_sum += put_gammas[i] * put_ois[i];
        }

        double net_gamma = call_sum - put_sum;
        return net_gamma * multiplier * (spot * spot) * 0.01 / 1000000.0;
    }

    static inline bool is_long_gamma_pinning(double net_gex_millions) {
        return net_gex_millions >= 0.0;
    }
};

} // namespace optionalpha
