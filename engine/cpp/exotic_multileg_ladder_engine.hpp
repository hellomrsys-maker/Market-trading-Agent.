#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Exotic Multi-Leg Ladder & Strip/Strap Engine (Ryan Bitstone).
 * sizeof(ExoticMultiLegLadderState) == 64 bytes exactly.
 */
struct alignas(64) ExoticMultiLegLadderState {
    double strike_rung1;            // 8 bytes
    double strike_rung2;            // 8 bytes
    double strike_rung3;            // 8 bytes
    double strike_rung4;            // 8 bytes
    double lambda_elasticity;       // 8 bytes
    double net_package_premium;     // 8 bytes
    double max_sweet_spot_profit;   // 8 bytes
    uint16_t strategy_archetype;    // 2 bytes (1=Strip, 2=Strap, 3=CallLadder, 4=PutLadder, 5=Butterfly, 6=Condor)
    uint8_t call_legs_count;        // 1 byte
    uint8_t put_legs_count;         // 1 byte
    uint8_t padding[4];             // 4 bytes padding -> 64 bytes
};

static_assert(sizeof(ExoticMultiLegLadderState) == 64, "ExoticMultiLegLadderState must be exactly 64 bytes!");

class ExoticMultiLegLadderEngineCpp {
public:
    static double compute_lambda(double delta, double spot, double option_price) {
        if (option_price <= 0.001) return 0.0;
        return (delta * spot) / option_price;
    }

    static ExoticMultiLegLadderState construct_strip(double spot, double atm_strike, double call_prem, double put_prem) {
        ExoticMultiLegLadderState state{};
        state.strike_rung1 = atm_strike;
        state.strike_rung2 = atm_strike;
        state.strike_rung3 = atm_strike;
        state.strike_rung4 = 0.0;
        state.net_package_premium = (2.0 * put_prem) + call_prem;
        double net_delta = (1.0 * 0.50) + (2.0 * (-0.50));
        state.lambda_elasticity = compute_lambda(net_delta, spot, state.net_package_premium);
        state.max_sweet_spot_profit = 999999.0;
        state.strategy_archetype = 1;
        state.call_legs_count = 1;
        state.put_legs_count = 2;
        return state;
    }

    static ExoticMultiLegLadderState construct_strap(double spot, double atm_strike, double call_prem, double put_prem) {
        ExoticMultiLegLadderState state{};
        state.strike_rung1 = atm_strike;
        state.strike_rung2 = atm_strike;
        state.strike_rung3 = atm_strike;
        state.strike_rung4 = 0.0;
        state.net_package_premium = (2.0 * call_prem) + put_prem;
        double net_delta = (2.0 * 0.50) + (1.0 * (-0.50));
        state.lambda_elasticity = compute_lambda(net_delta, spot, state.net_package_premium);
        state.max_sweet_spot_profit = 999999.0;
        state.strategy_archetype = 2;
        state.call_legs_count = 2;
        state.put_legs_count = 1;
        return state;
    }
};

} // namespace optionalpha
