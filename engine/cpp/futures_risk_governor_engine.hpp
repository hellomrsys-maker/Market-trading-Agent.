#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Futures Risk Governor.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) FuturesRiskState {
    double account_equity;           // 8 bytes
    double dollar_risk_target;       // 8 bytes
    double per_contract_risk;        // 8 bytes
    double current_heat_pct;         // 8 bytes
    double walk_forward_ratio;       // 8 bytes
    int32_t recommended_contracts;   // 4 bytes
    uint32_t is_deployable;          // 4 bytes (1 Robust, 0 Overfitted)
    uint32_t is_heat_compliant;      // 4 bytes (1 Compliant, 0 Exceeded)
    uint8_t padding[12];             // 12 bytes (total = 64 bytes)
};

static_assert(sizeof(FuturesRiskState) == 64, "FuturesRiskState must be exactly 64 bytes");

class FuturesRiskGovernorEngine {
public:
    static void compute_risk(
        FuturesRiskState& state,
        double equity,
        double risk_pct,
        double atr,
        double multiplier,
        double pt_val,
        double is_sharpe,
        double oos_sharpe,
        double open_risk_total
    ) {
        state.account_equity = equity;
        double clamped_risk = std::min(risk_pct, 1.5) / 100.0;
        state.dollar_risk_target = equity * clamped_risk;
        state.per_contract_risk = std::max(1.0, atr * multiplier * pt_val);
        state.recommended_contracts = std::max(1, static_cast<int32_t>(state.dollar_risk_target / state.per_contract_risk));

        double is_s = std::max(1e-4, is_sharpe);
        state.walk_forward_ratio = oos_sharpe / is_s;
        state.is_deployable = (state.walk_forward_ratio >= 0.65 && oos_sharpe > 0.5) ? 1 : 0;

        state.current_heat_pct = (open_risk_total / std::max(1.0, equity)) * 100.0;
        state.is_heat_compliant = (state.current_heat_pct <= 6.0) ? 1 : 0;
    }
};

} // namespace optionalpha
