#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Multi-Asset Cross-Market Liquidity & PDT Governor (Matthew Gray).
 * sizeof(CrossMarketPdtState) == 64 bytes exactly.
 */
struct alignas(64) CrossMarketPdtState {
    double account_equity;              // 8 bytes
    double margin_borrowed;             // 8 bytes
    double forex_leverage_ratio;        // 8 bytes
    double futures_tick_value;          // 8 bytes
    double max_risk_per_trade;          // 8 bytes
    double current_drawdown_pct;        // 8 bytes
    uint32_t round_trips_5d;            // 4 bytes
    uint16_t asset_class_id;            // 2 bytes
    uint8_t pdt_restricted;             // 1 byte
    uint8_t circuit_breaker_tripped;    // 1 byte
    uint8_t padding[8];                 // 8 bytes padding -> 64 bytes
};

static_assert(sizeof(CrossMarketPdtState) == 64, "CrossMarketPdtState must be exactly 64 bytes!");

class CrossMarketPdtEngineCpp {
public:
    static bool audit_compliance(CrossMarketPdtState& state, bool is_day_trade, double proposed_risk) {
        if (state.current_drawdown_pct >= 0.10) {
            state.circuit_breaker_tripped = 1;
            return false;
        }
        double risk_cap = state.account_equity * 0.05;
        if (proposed_risk > risk_cap) {
            return false;
        }
        if (state.account_equity < 25000.0 && is_day_trade) {
            if (state.round_trips_5d >= 3) {
                state.pdt_restricted = 1;
                return false;
            }
            state.round_trips_5d++;
        }
        return true;
    }
};

} // namespace optionalpha
