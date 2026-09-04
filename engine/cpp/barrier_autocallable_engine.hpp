// engine/cpp/barrier_autocallable_engine.hpp
// OptionAlpha Agent — Module V3: C++20 Barrier, Digital & Autocallable Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) BarrierAutocallableState {
    double shifted_barrier;
    double bs_digital_price;
    double skew_adjusted_digital;
    double autocall_coupon_paid;
    bool is_autocalled;
    char structure_tag[23]; // e.g. "AUTOCALL_REDEEMED"
    char pad[4];            // 64-byte alignment
};

class BarrierAutocallableEngineCpp {
private:
    static inline double normal_cdf(double z) {
        return 0.5 * std::erfc(-z / std::sqrt(2.0));
    }
    static inline double normal_pdf(double z) {
        return 0.3989422804014327 * std::exp(-0.5 * z * z);
    }

public:
    static inline BarrierAutocallableState evaluate_barrier_autocall_fast(
        double barrier, double sigma, double t, int num_obs, bool is_short_bar,
        double s, double x, double r, double skew,
        double current_perf, double autocall_trig, double coupon_trig, double coupon_pct
    ) {
        double dt = (num_obs > 0) ? (t / (double)num_obs) : t;
        double shift = 0.5826 * sigma * std::sqrt(dt);
        double shifted_h = barrier * std::exp(is_short_bar ? shift : -shift);

        double sqrt_t = std::sqrt(std::max(1e-6, t));
        double d1 = (std::log(s / x) + (r + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t);
        double d2 = d1 - sigma * sqrt_t;

        double vega = s * normal_pdf(d1) * sqrt_t;
        double bs_dig = std::exp(-r * t) * normal_cdf(d2);
        double skew_dig = bs_dig + vega * std::abs(skew);

        bool autocalled = current_perf >= autocall_trig;
        double c_paid = autocalled ? coupon_pct : (current_perf >= coupon_trig ? coupon_pct : 0.0);

        BarrierAutocallableState state{};
        state.shifted_barrier = shifted_h;
        state.bs_digital_price = bs_dig;
        state.skew_adjusted_digital = skew_dig;
        state.autocall_coupon_paid = c_paid;
        state.is_autocalled = autocalled;
        return state;
    }
};

} // namespace optionalpha
