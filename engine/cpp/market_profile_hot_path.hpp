// engine/cpp/market_profile_hot_path.hpp
// OptionAlpha Agent — C++20 Zero-Bridge Hot-Path Market Profile & Auction Open Classifier
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <algorithm>
#include <cmath>

namespace optionalpha {

class MarketProfileHotPathEngine {
public:
    static inline void compute_value_area(double day_high, double day_low, double& poc, double& vah, double& val) {
        poc = (day_high + day_low) / 2.0;
        double half_width = (day_high - day_low) * 0.35;
        vah = poc + half_width;
        val = poc - half_width;
    }

    static inline bool is_open_drive(double open, double high, double low, double close) {
        double range = std::max(1e-4, high - low);
        return (std::abs(close - open) / range) > 0.75;
    }
};

} // namespace optionalpha
