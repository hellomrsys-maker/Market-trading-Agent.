// engine/cpp/psychological_governor_hot_path.hpp
// OptionAlpha Agent — C++20 Zero-Bridge Hot-Path Disciplined Trader Governor
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <algorithm>

namespace optionalpha {

class PsychologicalHotPathGovernor {
public:
    static inline bool validate_disciplined_trade(double stop_loss, double equity, double risk_dollars, double max_risk_pct = 0.02) {
        if (stop_loss <= 0.0) return false;
        double max_allowed = equity * max_risk_pct;
        return risk_dollars <= max_allowed * 1.05;
    }

    static inline double get_adaptive_scaling(int32_t consecutive_wins, int32_t consecutive_losses) {
        if (consecutive_losses >= 3) return 0.50; // Suppress tilt/revenge
        if (consecutive_wins >= 4) return 0.75;  // Suppress euphoria
        return 1.0;
    }
};

} // namespace optionalpha
