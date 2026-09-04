// engine/cpp/smc_expectancy_engine.hpp
// OptionAlpha Agent — Module M3: C++20 SMC & Expectancy Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>

namespace optionalpha {

struct alignas(64) SMCExpectancyState {
    double system_expectancy_r;
    double half_kelly_risk_pct;
    double ob_displacement_ratio;
    bool is_valid_unmitigated_ob;
    bool is_choch_warning;
    char structure_tag[18]; // e.g. "BOS_BULLISH"
    char pad[6];            // 64-byte alignment
};

class SMCExpectancyEngineCpp {
public:
    static inline SMCExpectancyState evaluate_smc_fast(
        double win_rate,
        double avg_win,
        double avg_loss,
        double displacement_ratio,
        bool is_mitigated,
        bool is_choch
    ) {
        double loss_rate = 1.0 - win_rate;
        double exp = (win_rate * avg_win) - (loss_rate * avg_loss);
        double b = avg_win / std::max(0.01, avg_loss);
        double kelly = (b * win_rate - loss_rate) / b;
        double half_kelly = std::max(0.0, kelly / 2.0);

        SMCExpectancyState state{};
        state.system_expectancy_r = exp;
        state.half_kelly_risk_pct = std::min(2.0, half_kelly * 100.0);
        state.ob_displacement_ratio = displacement_ratio;
        state.is_valid_unmitigated_ob = (displacement_ratio >= 2.0) && (!is_mitigated);
        state.is_choch_warning = is_choch;
        return state;
    }
};

} // namespace optionalpha
