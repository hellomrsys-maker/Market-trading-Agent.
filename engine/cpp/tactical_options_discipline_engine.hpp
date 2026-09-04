#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Options Structuring & Discipline.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) TacticalOptionsDisciplineState {
    float account_equity;           // 4 bytes
    float max_dollar_risk;          // 4 bytes
    float entry_price;              // 4 bytes
    float stop_loss_price;          // 4 bytes
    float take_profit_price;        // 4 bytes
    float iron_condor_net_credit;   // 4 bytes
    float iron_condor_max_loss;     // 4 bytes
    float iron_condor_rr;           // 4 bytes
    uint32_t recommended_shares;    // 4 bytes
    uint32_t recommended_contracts; // 4 bytes
    uint32_t oco_active_status;     // 4 bytes (0: inactive, 1: active, 2: filled_tp, 3: filled_sl)
    uint32_t discipline_lock_flag;  // 4 bytes (0: ok, 1: locked)
    uint8_t padding[16];            // 16 bytes padding -> Total 64 bytes
};

static_assert(sizeof(TacticalOptionsDisciplineState) == 64, "TacticalOptionsDisciplineState must be exactly 64 bytes for Zero-Bridge synchronization");

class TacticalOptionsDisciplineEngine {
public:
    static void compute_sizing_and_condor(
        TacticalOptionsDisciplineState& state,
        float equity,
        float entry,
        float stop,
        float tp,
        float k1, float k2, float k3, float k4,
        float p_short, float p_long, float c_short, float c_long
    ) {
        state.account_equity = equity;
        state.entry_price = entry;
        state.stop_loss_price = stop;
        state.take_profit_price = tp;
        
        // 1-2% risk sizing
        float risk_fraction = 0.01f;
        state.max_dollar_risk = equity * risk_fraction;
        float per_share_risk = std::abs(entry - stop);
        state.recommended_shares = per_share_risk > 0.0f ? static_cast<uint32_t>(state.max_dollar_risk / per_share_risk) : 0;
        state.recommended_contracts = state.recommended_shares / 100;

        // Iron Condor calculation
        float put_credit = p_short - p_long;
        float call_credit = c_short - c_long;
        state.iron_condor_net_credit = (put_credit + call_credit) * 100.0f;
        float wing_width = (k2 - k1) * 100.0f;
        state.iron_condor_max_loss = std::max(0.0f, wing_width - state.iron_condor_net_credit);
        state.iron_condor_rr = state.iron_condor_max_loss > 0.0f ? state.iron_condor_net_credit / state.iron_condor_max_loss : 0.0f;

        state.oco_active_status = 1;
        state.discipline_lock_flag = 0;
    }
};

} // namespace optionalpha
