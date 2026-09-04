#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Options Equivalency & Synthetics.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) OptionsEquivalencyState {
    float stock_price;              // 4 bytes
    float strike_price;             // 4 bytes
    float carry_cost;               // 4 bytes
    float dividend_amount;          // 4 bytes
    float basis_value;              // 4 bytes
    float forward_price;            // 4 bytes
    float theoretical_stock_parity; // 4 bytes
    float synthetic_call_value;     // 4 bytes
    float synthetic_put_value;      // 4 bytes
    float box_spread_profit;        // 4 bytes
    uint32_t is_arbitrage_present;  // 4 bytes
    uint32_t parity_achieved_flag;  // 4 bytes
    uint8_t padding[16];            // 16 bytes padding -> Total 64 bytes
};

static_assert(sizeof(OptionsEquivalencyState) == 64, "OptionsEquivalencyState must be exactly 64 bytes for Zero-Bridge synchronization");

class OptionsEquivalencyEngine {
public:
    static void compute_equivalency(
        OptionsEquivalencyState& state,
        float s, float k, float c, float p,
        float r, int days, float div
    ) {
        state.stock_price = s;
        state.strike_price = k;
        state.dividend_amount = div;

        float t = static_cast<float>(days) / 360.0f;
        state.carry_cost = s * r * t;
        state.basis_value = state.carry_cost - div;
        state.forward_price = s + state.basis_value;

        state.theoretical_stock_parity = c - p + k - state.basis_value;
        state.synthetic_call_value = s - k + p + state.basis_value;
        state.synthetic_put_value = c + k - s - state.basis_value;

        float disc = std::abs(s - state.theoretical_stock_parity);
        state.is_arbitrage_present = disc > 0.05f ? 1 : 0;
        state.parity_achieved_flag = disc <= 0.05f ? 1 : 0;
    }
};

} // namespace optionalpha
