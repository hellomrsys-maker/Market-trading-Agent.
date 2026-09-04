#pragma once
#include "../cpp/zero_bridge.hpp"

namespace optionalpha {
struct alignas(64) VantageForexState {
    double rsi_divergence_score;
    bool is_hawkish;
    char pad[47]; 
};

class VantageForexEngineCpp {
public:
    static inline VantageForexState analyze_sentiment(bool hawkish, double rsi) {
        return {rsi, hawkish, {0}};
    }
};
}
