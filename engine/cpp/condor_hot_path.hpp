// engine/cpp/condor_hot_path.hpp
// OptionAlpha Agent — C++20 Hot-Path Iron Condor Margin & Breach Monitor
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <algorithm>

namespace optionalpha {

class CondorHotPathEngine {
public:
    static inline double calculate_condor_margin_dollars(double put_wing_width, double call_wing_width, double net_credit, double multiplier = 100.0) {
        double max_wing = std::max(put_wing_width, call_wing_width);
        return (max_wing - net_credit) * multiplier;
    }

    static inline bool is_wing_threatened(double spot, double short_put, double short_call, double buffer_pct = 0.01) {
        if (spot <= short_put * (1.0 + buffer_pct)) return true;
        if (spot >= short_call * (1.0 - buffer_pct)) return true;
        return false;
    }
};

} // namespace optionalpha
