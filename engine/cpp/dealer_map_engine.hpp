#pragma once

namespace optionalpha {
struct alignas(64) DealerMapState {
    double max_pain;
    bool is_long_gamma;
    char pad[55];
};

class DealerMapEngineCpp {
public:
    static inline DealerMapState get_state() { return {0.0, false, {0}}; }
};
}
