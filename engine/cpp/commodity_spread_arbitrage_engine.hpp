#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Commodity Processing & Spreads.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) CommoditySpreadState {
    double crude_oil_price;          // 8 bytes
    double energy_crack_margin;      // 8 bytes
    double soybean_price;            // 8 bytes
    double soybean_crush_gpm;        // 8 bytes
    double cost_of_carry_fair_val;   // 8 bytes
    int32_t crack_signal;            // 4 bytes (+1 Buy Spread, -1 Sell Spread, 0 Hold)
    int32_t crush_signal;            // 4 bytes (+1 Buy Beans, -1 Sell Beans, 0 Hold)
    uint32_t contango_flag;          // 4 bytes (1 Contango, 0 Backwardation)
    uint8_t padding[12];             // 12 bytes (total = 64 bytes)
};

static_assert(sizeof(CommoditySpreadState) == 64, "CommoditySpreadState must be exactly 64 bytes");

class CommoditySpreadArbitrageEngine {
public:
    static void compute_spreads(
        CommoditySpreadState& state,
        double cl, double rbob, double ho,
        double beans, double meal, double oil,
        double spot, double carry_rate, double t
    ) {
        state.crude_oil_price = cl;
        state.soybean_price = beans;

        // 3:2:1 Crack
        double gas_bbl = rbob * 42.0;
        double ho_bbl = ho * 42.0;
        state.energy_crack_margin = ((2.0 * gas_bbl + ho_bbl) - (3.0 * cl)) / 3.0;
        if (state.energy_crack_margin >= 25.0) {
            state.crack_signal = -1; // Sell crack
        } else if (state.energy_crack_margin <= 10.0) {
            state.crack_signal = 1;  // Buy crack
        } else {
            state.crack_signal = 0;
        }

        // Crush GPM
        double meal_rev = meal * 2.2;
        double oil_rev = oil * 11.0;
        state.soybean_crush_gpm = (meal_rev + oil_rev) - beans;
        if (state.soybean_crush_gpm > 180.0) {
            state.crush_signal = -1; // Reverse crush
        } else if (state.soybean_crush_gpm < 60.0) {
            state.crush_signal = 1;  // Crush
        } else {
            state.crush_signal = 0;
        }

        // Cost of carry
        state.cost_of_carry_fair_val = spot * std::exp(carry_rate * t);
        state.contango_flag = (carry_rate > 0.0) ? 1 : 0;
    }
};

} // namespace optionalpha
