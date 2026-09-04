// engine/cpp/dispersion_rainbow_engine.hpp
// OptionAlpha Agent — Module U3: C++20 Dispersion, Rainbow & Basket Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) DispersionRainbowState {
    double basket_variance;
    double rainbow_payoff;
    double best_of_call_parity;
    double icbc_payoff;
    double cbc_payoff;
    double dispersion_benefit;
    char basket_tag[12]; // e.g. "RAINBOW_50"
    char pad[4];         // 64-byte alignment
};

class DispersionRainbowEngineCpp {
public:
    static inline DispersionRainbowState evaluate_dispersion_fast(
        double var_p, double call1, double call2, double wo_call,
        double r1, double r2, double r3, double cap
    ) {
        double bo_parity = call1 + call2 - wo_call;
        double arr[3] = {r1, r2, r3};
        std::sort(arr, arr + 3, std::greater<double>());
        double rainbow = 0.5 * arr[0] + 0.3 * arr[1] + 0.2 * arr[2];

        double icbc = (std::min(r1, cap) + std::min(r2, cap) + std::min(r3, cap)) / 3.0;
        double cbc = std::min((r1 + r2 + r3) / 3.0, cap);

        DispersionRainbowState state{};
        state.basket_variance = var_p;
        state.rainbow_payoff = std::max(0.0, rainbow);
        state.best_of_call_parity = bo_parity;
        state.icbc_payoff = std::max(0.0, icbc);
        state.cbc_payoff = std::max(0.0, cbc);
        state.dispersion_benefit = cbc - icbc;
        return state;
    }
};

} // namespace optionalpha
