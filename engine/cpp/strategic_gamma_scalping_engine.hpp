#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Strategic Gamma Scalping & Position Adjustment.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) StrategicGammaScalpingState {
    float spot_price;               // 4 bytes
    float last_hedge_spot;          // 4 bytes
    float position_gamma;           // 4 bytes
    float daily_theta_rent;         // 4 bytes
    float gamma_decay_breakeven;    // 4 bytes (Delta_S = sqrt(2*Theta/Gamma))
    float daily_one_sigma_move;     // 4 bytes
    float net_delta;                // 4 bytes
    int32_t rebalance_shares_needed;// 4 bytes
    uint32_t roll_operation_id;     // 4 bytes (0: None, 1: Roll Call, 2: Roll Put, 3: Roll Fly)
    uint32_t staying_alive_flag;    // 4 bytes (1: Spread active, 0: Naked risk)
    uint8_t padding[24];            // 24 bytes padding -> Total 64 bytes
};

static_assert(sizeof(StrategicGammaScalpingState) == 64, "StrategicGammaScalpingState must be exactly 64 bytes for Zero-Bridge synchronization");

class StrategicGammaScalpingEngine {
public:
    static void execute_scalp_evaluation(
        StrategicGammaScalpingState& state,
        float spot, float last_hedge,
        float gamma, float theta, float net_delta,
        float annual_vol
    ) {
        state.spot_price = spot;
        state.last_hedge_spot = last_hedge;
        state.position_gamma = std::max(1e-6f, gamma);
        state.daily_theta_rent = std::abs(theta);
        state.net_delta = net_delta;

        // Breakeven Move Delta_S = sqrt(2*Theta/Gamma)
        state.gamma_decay_breakeven = std::sqrt((2.0f * state.daily_theta_rent) / state.position_gamma);

        // 1-Sigma daily move
        float daily_vol = annual_vol / std::sqrt(252.0f);
        state.daily_one_sigma_move = spot * daily_vol;

        float move = spot - last_hedge;
        if (std::abs(move) >= 2.0f) {
            state.rebalance_shares_needed = -static_cast<int32_t>(net_delta * 100.0f);
        } else {
            state.rebalance_shares_needed = 0;
        }

        state.staying_alive_flag = 1;
        state.roll_operation_id = 1;
    }
};

} // namespace optionalpha
