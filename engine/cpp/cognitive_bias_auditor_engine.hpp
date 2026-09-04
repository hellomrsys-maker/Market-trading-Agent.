// engine/cpp/cognitive_bias_auditor_engine.hpp
// OptionAlpha Agent — Module P3: C++20 Cognitive Bias Circuit Breaker Core
#pragma once

#include "zero_bridge.hpp"

namespace optionalpha {

struct alignas(64) CognitiveBiasState {
    double size_multiplier;
    int stress_level;
    int focus_level;
    bool is_trade_allowed;
    bool is_revenge_risk;
    char bias_alert[22]; // e.g. "REVENGE_TRADING_LOCK"
    char pad[22];        // 64-byte alignment
};

class CognitiveBiasAuditorEngineCpp {
public:
    static inline CognitiveBiasState check_mental_state(
        int stress,
        int focus,
        int time_since_loss_mins
    ) {
        bool revenge = (time_since_loss_mins < 30);
        bool allowed = (stress <= 6) && (focus >= 5) && (!revenge);
        double mult = allowed ? 1.0 : (revenge ? 0.0 : 0.5);

        CognitiveBiasState state{};
        state.size_multiplier = mult;
        state.stress_level = stress;
        state.focus_level = focus;
        state.is_trade_allowed = allowed;
        state.is_revenge_risk = revenge;
        return state;
    }
};

} // namespace optionalpha
