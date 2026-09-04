// engine/cpp/calendar_hot_path.hpp
// OptionAlpha Agent — C++20 Hot-Path Calendar Spread Theta & Risk Gate
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"

namespace optionalpha {

class CalendarHotPathEngine {
public:
    static inline double compute_calendar_max_loss(double net_debit, double multiplier = 100.0) {
        return net_debit * multiplier;
    }

    static inline bool validate_term_backwardation(double near_iv, double far_iv, double min_spread = 0.02) {
        return (near_iv - far_iv) >= min_spread;
    }
};

} // namespace optionalpha
