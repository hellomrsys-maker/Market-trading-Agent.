#pragma once

namespace optionalpha {
struct alignas(64) MinerHighProbabilityState {
    double target_price;
    double max_capital_exposure;
    int position_size;
    char pad[44];
};

class MinerHighProbabilityEngineCpp {
public:
    static inline MinerHighProbabilityState calculate_trade(double capital, double entry, double stop) {
        double max_risk = capital * 0.03;
        double risk_per_unit = entry > stop ? entry - stop : stop - entry;
        int size = risk_per_unit > 0 ? (int)(max_risk / risk_per_unit) : 0;
        return {0.0, max_risk, size, {0}};
    }
};
}
