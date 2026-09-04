#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Cash Flow & Capital Ecosystem.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) CashflowCapitalState {
    float total_income;             // 4 bytes
    float fixed_essentials;         // 4 bytes
    float variable_essentials;      // 4 bytes
    float sinking_funds_total;      // 4 bytes
    float workable_total;           // 4 bytes
    float keep_savings_allocated;   // 4 bytes
    float spend_discretionary;      // 4 bytes
    float new_zero_buffer;          // 4 bytes
    float intentional_spend_ratio;  // 4 bytes
    float weighted_joy_score;       // 4 bytes
    uint32_t is_leaking_detected;   // 4 bytes
    uint32_t values_aligned_flag;   // 4 bytes
    uint8_t padding[16];            // 16 bytes padding -> Total 64 bytes
};

static_assert(sizeof(CashflowCapitalState) == 64, "CashflowCapitalState must be exactly 64 bytes for Zero-Bridge synchronization");

class CashflowCapitalEcosystemEngine {
public:
    static void compute_ecosystem(
        CashflowCapitalState& state,
        float income,
        float fixed_costs,
        float variable_costs,
        float sinking_total,
        float savings_ratio,
        float new_zero
    ) {
        state.total_income = income;
        state.fixed_essentials = fixed_costs;
        state.variable_essentials = variable_costs;
        state.sinking_funds_total = sinking_total;
        state.new_zero_buffer = new_zero;

        float total_essentials = fixed_costs + variable_costs + sinking_total;
        state.workable_total = std::max(0.0f, income - total_essentials);
        state.keep_savings_allocated = state.workable_total * savings_ratio;
        state.spend_discretionary = std::max(0.0f, state.workable_total - state.keep_savings_allocated);
        state.values_aligned_flag = (state.keep_savings_allocated > 0.0f && state.workable_total > 0.0f) ? 1 : 0;
    }
};

} // namespace optionalpha
