#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Pattern Alignment & Risk Governor.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) PatternAlignmentRiskState {
    double entry_price;              // 8 bytes
    double target_price;             // 8 bytes
    double stop_loss_price;          // 8 bytes
    double reward_points;            // 8 bytes
    double risk_points;              // 8 bytes
    double risk_to_reward_ratio;     // 8 bytes
    uint32_t is_rr_approved;         // 4 bytes
    uint32_t is_htf_aligned;         // 4 bytes
    uint32_t is_trade_approved;      // 4 bytes
    uint8_t padding[4];              // 4 bytes (total = 64 bytes)
};

static_assert(sizeof(PatternAlignmentRiskState) == 64, "PatternAlignmentRiskState must be exactly 64 bytes");

class PatternAlignmentRiskGovernor {
public:
    static void audit_risk_reward(
        PatternAlignmentRiskState& state,
        double entry,
        double target,
        double stop,
        int32_t htf_dir,
        int32_t pattern_dir
    ) {
        state.entry_price = entry;
        state.target_price = target;
        state.stop_loss_price = stop;
        state.reward_points = std::abs(target - entry);
        state.risk_points = std::abs(entry - stop);

        state.risk_to_reward_ratio = state.reward_points / std::max(1e-4, state.risk_points);
        state.is_rr_approved = (state.risk_to_reward_ratio >= 2.0) ? 1 : 0;
        state.is_htf_aligned = (htf_dir == pattern_dir || htf_dir == 0) ? 1 : 0;

        state.is_trade_approved = (state.is_rr_approved && state.is_htf_aligned) ? 1 : 0;
    }
};

} // namespace optionalpha
