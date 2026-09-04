#pragma once

namespace optionalpha {
struct alignas(64) OrderFlowState {
    double limit_buy_imbalance;
    bool is_long_buildup;
    char pad[55];
};

class OrderFlowEngineCpp {
public:
    static inline OrderFlowState get_state() { return {0.0, false, {0}}; }
};
}
