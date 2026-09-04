// engine/cpp/forex_hot_path.hpp
// OptionAlpha Agent — C++20 Zero-Bridge Hot-Path Forex Pip Valuation & Margin Sizing Engine
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <algorithm>
#include <cmath>

namespace optionalpha {

class ForexHotPathEngine {
public:
    static inline double compute_pip_value(double units, double spot, bool is_jpy = false, bool is_usd_quote = true) {
        double scale = is_jpy ? 0.01 : 0.0001;
        if (is_usd_quote) {
            return scale * units;
        } else {
            return (scale * units) / std::max(1e-4, spot);
        }
    }

    static inline double compute_safe_lots(double equity, double risk_pct, double stop_loss_pips, double pip_val_one_lot) {
        double safe_pct = std::clamp(risk_pct, 0.005, 0.02);
        double max_risk_dlrs = equity * safe_pct;
        double risk_per_lot = stop_loss_pips * pip_val_one_lot;
        if (risk_per_lot <= 0.0) return 0.01;
        return std::max(0.01, max_risk_dlrs / risk_per_lot);
    }
};

} // namespace optionalpha
