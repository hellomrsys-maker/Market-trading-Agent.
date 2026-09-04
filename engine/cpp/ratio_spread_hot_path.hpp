// engine/cpp/ratio_spread_hot_path.hpp
// OptionAlpha Agent — C++20 Hot-Path Put Ratio Spread (1x2) Margin & Downside Tail Gate
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"

namespace optionalpha {

class RatioSpreadHotPathEngine {
public:
    static inline double compute_max_profit(double long_strike, double short_strike, double net_credit_or_debit, double multiplier = 100.0) {
        return ((long_strike - short_strike) + net_credit_or_debit) * multiplier;
    }

    static inline double compute_lower_breakeven(double long_strike, double short_strike, double net_credit_or_debit) {
        return short_strike - (long_strike - short_strike) - net_credit_or_debit;
    }
};

} // namespace optionalpha
