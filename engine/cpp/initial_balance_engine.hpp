#pragma once

namespace optionalpha {
struct alignas(64) InitialBalanceState {
    double ib_range;
    bool is_trend_day;
    char pad[55];
};

class InitialBalanceEngineCpp {
public:
    static inline InitialBalanceState get_state() { return {0.0, false, {0}}; }
};
}
