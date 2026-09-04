#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Asymmetric 1:2 Ratio Backspread Engine (Frank Richmond).
 * sizeof(RatioBackspreadState) == 64 bytes exactly.
 */
struct alignas(64) RatioBackspreadState {
    double short_strike;        // 8 bytes
    double long_strike;         // 8 bytes
    double net_debit_credit;    // 8 bytes
    double max_loss_point;      // 8 bytes
    double upper_bep;           // 8 bytes
    double lower_bep;           // 8 bytes
    double implied_volatility;  // 8 bytes
    uint16_t ratio_short;       // 2 bytes
    uint16_t ratio_long;        // 2 bytes
    uint8_t is_call_spread;     // 1 byte
    uint8_t padding[3];         // 3 bytes padding -> 64 bytes
};

static_assert(sizeof(RatioBackspreadState) == 64, "RatioBackspreadState must be exactly 64 bytes!");

class RatioBackspreadEngineCpp {
public:
    static RatioBackspreadState construct(double atm_strike, double otm_strike, double short_prem, double long_prem, bool is_call) {
        RatioBackspreadState state{};
        state.short_strike = atm_strike;
        state.long_strike = otm_strike;
        state.net_debit_credit = (2.0 * long_prem) - short_prem;
        state.max_loss_point = std::abs(otm_strike - atm_strike) + state.net_debit_credit;
        state.upper_bep = otm_strike + state.max_loss_point;
        state.lower_bep = atm_strike + (state.net_debit_credit < 0.0 ? state.net_debit_credit : 0.0);
        state.implied_volatility = 0.30;
        state.ratio_short = 1;
        state.ratio_long = 2;
        state.is_call_spread = is_call ? 1 : 0;
        return state;
    }

    static double calculate_terminal_pnl(const RatioBackspreadState& state, double st) {
        if (state.is_call_spread) {
            double short_val = std::max(0.0, st - state.short_strike);
            double long_val = 2.0 * std::max(0.0, st - state.long_strike);
            return (long_val - short_val) - state.net_debit_credit;
        } else {
            double short_val = std::max(0.0, state.short_strike - st);
            double long_val = 2.0 * std::max(0.0, state.long_strike - st);
            return (long_val - short_val) - state.net_debit_credit;
        }
    }
};

} // namespace optionalpha
