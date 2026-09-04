// engine/cpp/candlestick_hot_path.hpp
// OptionAlpha Agent — C++20 Hot-Path Candlestick Pattern Recognition
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <cmath>

namespace optionalpha {

class CandlestickHotPathEngine {
public:
    static inline bool is_morning_star(double o1, double c1, double o2, double c2, double o3, double c3) {
        bool b1_bear = c1 < o1;
        double b1_body = std::abs(c1 - o1);
        double b2_body = std::abs(c2 - o2);
        bool b3_bull = c3 > o3;
        return b1_bear && (b2_body < b1_body * 0.35) && b3_bull && (c3 >= o1 - (b1_body * 0.40));
    }

    static inline bool is_evening_star(double o1, double c1, double o2, double c2, double o3, double c3) {
        bool b1_bull = c1 > o1;
        double b1_body = std::abs(c1 - o1);
        double b2_body = std::abs(c2 - o2);
        bool b3_bear = c3 < o3;
        return b1_bull && (b2_body < b1_body * 0.35) && b3_bear && (c3 <= o1 + (b1_body * 0.40));
    }

    static inline bool is_bullish_engulfing(double o2, double c2, double o3, double c3) {
        return (c2 < o2) && (c3 > o3) && (o3 <= c2) && (c3 >= o2);
    }

    static inline bool is_bearish_engulfing(double o2, double c2, double o3, double c3) {
        return (c2 > o2) && (c3 < o3) && (o3 >= c2) && (c3 <= o2);
    }
};

} // namespace optionalpha
