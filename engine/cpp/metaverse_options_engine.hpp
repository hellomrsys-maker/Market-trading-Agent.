#pragma once

namespace optionalpha {
struct alignas(64) MetaverseOptionsState {
    double point_of_control;
    double ask_bid_delta;
    char pad[48]; 
};

class MetaverseOptionsEngineCpp {
public:
    static inline MetaverseOptionsState track_order_flow(double call_delta, double put_delta) {
        return {0.0, call_delta - put_delta, {0}};
    }
};
}
