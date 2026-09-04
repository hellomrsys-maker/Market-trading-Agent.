// engine/cpp/bsm_jump_diffusion_engine.hpp
// OptionAlpha Agent — Module R3: C++20 BSM & Jump-Diffusion Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) BSMJumpDiffusionState {
    double call_price;
    double put_price;
    double delta_call;
    double elasticity_call;
    double prob_ever_itm;
    double regrets_interest_on_strike;
    char model_tag[12]; // e.g. "BSM_MERTON"
    char pad[4];        // 64-byte alignment
};

class BSMJumpDiffusionEngineCpp {
private:
    static inline double normal_cdf(double z) {
        return 0.5 * std::erfc(-z / std::sqrt(2.0));
    }

public:
    static inline BSMJumpDiffusionState price_merton_fast(
        double s, double x, double t, double r, double sigma, double q
    ) {
        double sqrt_t = std::sqrt(std::max(1e-6, t));
        double d1 = (std::log(s / x) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t);
        double d2 = d1 - sigma * sqrt_t;

        double nd1 = normal_cdf(d1);
        double nd2 = normal_cdf(d2);
        double exp_qt = std::exp(-q * t);
        double exp_rt = std::exp(-r * t);

        double call = s * exp_qt * nd1 - x * exp_rt * nd2;
        double put = x * exp_rt * normal_cdf(-d2) - s * exp_qt * normal_cdf(-d1);
        double delta_call = exp_qt * nd1;
        double elasticity = (s * delta_call) / std::max(1e-4, call);

        // First-Passage Prob Ever ITM
        double b = (1.0 / sigma) * std::log(x / s);
        double a = (1.0 / sigma) * (r - q - 0.5 * sigma * sigma);
        double p_ever = (s >= x) ? 1.0 : (nd2 + std::exp(2.0 * a * b) * normal_cdf(d2 - 2.0 * a * sqrt_t));

        BSMJumpDiffusionState state{};
        state.call_price = call;
        state.put_price = put;
        state.delta_call = delta_call;
        state.elasticity_call = elasticity;
        state.prob_ever_itm = std::min(1.0, std::max(0.0, p_ever));
        state.regrets_interest_on_strike = x * (1.0 - exp_rt);
        return state;
    }
};

} // namespace optionalpha
