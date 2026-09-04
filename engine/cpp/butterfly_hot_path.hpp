// engine/cpp/butterfly_hot_path.hpp
// OptionAlpha Agent — C++20 Hot-Path Iron Butterfly Pin & Risk Gate
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

class ButterflyHotPathEngine {
public:
    static inline double compute_max_loss(double wing_width, double net_credit, double multiplier = 100.0) {
        return (wing_width - net_credit) * multiplier;
    }

    static inline bool is_pin_breached(double spot, double atm_strike, double net_credit) {
        return std::abs(spot - atm_strike) > net_credit;
    }
};

} // namespace optionalpha
