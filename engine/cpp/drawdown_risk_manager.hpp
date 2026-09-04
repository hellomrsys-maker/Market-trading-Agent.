// engine/cpp/drawdown_risk_manager.hpp
// OptionAlpha Agent — Module T_sys3: C++20 Drawdown Risk Manager Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) DrawdownRiskState {
    double current_capital;
    double peak_equity;
    double pct_drawdown;
    double max_dd_cutoff_pct;
    int calculated_position_size;
    int consecutive_losses;
    bool is_system_halted;
    char status_tag[15]; // e.g. "HEALTHY"
    char pad[1];         // 64-byte alignment
};

class DrawdownRiskManagerCpp {
public:
    static inline DrawdownRiskState evaluate_risk_fast(
        double current_cap,
        double peak_eq,
        double pnl,
        int prev_consecutive_losses,
        double max_dd_cutoff,
        double risk_pct,
        double max_loss_per_contract
    ) {
        double new_cap = current_cap + pnl;
        double new_peak = std::max(peak_eq, new_cap);
        int consec = (pnl < 0) ? (prev_consecutive_losses + 1) : 0;
        double dollar_dd = new_peak - new_cap;
        double pct_dd = (new_peak > 0) ? (dollar_dd / new_peak) * 100.0 : 0.0;

        bool halted = (pct_dd >= max_dd_cutoff) || (consec >= 6);

        double max_dollar_risk = new_cap * (risk_pct / 100.0);
        int pos_size = (max_loss_per_contract > 0) ? (int)std::max(1.0, std::floor(max_dollar_risk / max_loss_per_contract)) : 1;

        DrawdownRiskState state{};
        state.current_capital = new_cap;
        state.peak_equity = new_peak;
        state.pct_drawdown = pct_dd;
        state.max_dd_cutoff_pct = max_dd_cutoff;
        state.calculated_position_size = pos_size;
        state.consecutive_losses = consec;
        state.is_system_halted = halted;
        return state;
    }
};

} // namespace optionalpha
