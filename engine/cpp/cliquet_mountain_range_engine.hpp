// engine/cpp/cliquet_mountain_range_engine.hpp
// OptionAlpha Agent — Module W3: C++20 Cliquet, Napoleon & Mountain Range Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) CliquetMountainState {
    double lflc_cliquet_payoff;
    double gflc_cliquet_payoff;
    double napoleon_payoff;
    double everest_payoff;
    double himalaya_payoff;
    char cliquet_tag[16]; // e.g. "GFLC_ACTIVE"
    char pad[8];          // 64-byte alignment
};

class CliquetMountainRangeEngineCpp {
public:
    static inline CliquetMountainState evaluate_cliquet_mountain_fast(
        double r1, double r2, double r3,
        double local_floor, double local_cap,
        double global_floor, double global_cap,
        double max_coupon, double everest_coupon
    ) {
        double c1 = std::max(local_floor, std::min(r1, local_cap));
        double c2 = std::max(local_floor, std::min(r2, local_cap));
        double c3 = std::max(local_floor, std::min(r3, local_cap));
        double lflc = c1 + c2 + c3;
        double gflc = std::max(global_floor, std::min(global_cap, lflc));

        double worst_r = std::min({r1, r2, r3});
        double napoleon = std::max(0.0, max_coupon + worst_r);
        double everest = everest_coupon + worst_r;

        CliquetMountainState state{};
        state.lflc_cliquet_payoff = lflc;
        state.gflc_cliquet_payoff = gflc;
        state.napoleon_payoff = napoleon;
        state.everest_payoff = everest;
        state.himalaya_payoff = std::max({r1, r2, r3});
        return state;
    }
};

} // namespace optionalpha
