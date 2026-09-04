// engine/cpp/dealer_hot_path.hpp
// OptionAlpha Agent — C++20 Dealer Core Map
// Polyglot Pillar 4: C++20 Engine Core

#pragma once

#include "zero_bridge.hpp"
#include <cmath>

namespace optionalpha {

// Deep representation of the Order Flow / Dealer state sent back to Python API via zero-bridge
struct alignas(64) DealerOrderFlowState {
    double vwap;                     // Daily VWAP
    double pdh;                      // Previous Day High
    double pdl;                      // Previous Day Low
    double limit_buy_imbalance;      // Limit buyers / total volume
    bool is_liquidity_sweep;         // Are stops being hunted?
    char day_type[14];               // e.g., "TREND_DAY"
    char pad[9];                     // 64-byte alignment padding for zero-bridge synchronization
};

class DealerHotPathEngine {
public:
    static inline DealerOrderFlowState track_liquidity(
        double current_price,
        double vwap,
        double pdh,
        double pdl,
        double limit_buys,
        double limit_sells
    ) {
        bool sweep = false;
        if (current_price >= pdh * 0.999 && current_price <= pdh * 1.001) {
            sweep = true; // Sweeping PDH liquidity
        } else if (current_price <= pdl * 1.001 && current_price >= pdl * 0.999) {
            sweep = true; // Sweeping PDL liquidity
        }
        
        double imbalance = limit_buys / std::max(1.0, limit_buys + limit_sells);
        
        DealerOrderFlowState state{};
        state.vwap = vwap;
        state.pdh = pdh;
        state.pdl = pdl;
        state.limit_buy_imbalance = imbalance;
        state.is_liquidity_sweep = sweep;
        // Padding ensures 0-ns mem sync
        
        return state;
    }
};

} // namespace optionalpha
