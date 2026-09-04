#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Retail Income Risk Governor.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) RetailIncomeRiskState {
    double account_equity;           // 8 bytes
    double max_symbol_allocation;    // 8 bytes
    double total_symbol_exposure;    // 8 bytes
    double remaining_cash_buffer_pct;// 8 bytes
    int32_t days_to_earnings;        // 4 bytes
    uint32_t is_symbol_cap_ok;       // 4 bytes
    uint32_t is_cash_buffer_ok;      // 4 bytes
    uint32_t is_earnings_safe;       // 4 bytes
    uint32_t is_trade_approved;      // 4 bytes
    uint8_t padding[12];             // 12 bytes (total = 64 bytes)
};

static_assert(sizeof(RetailIncomeRiskState) == 64, "RetailIncomeRiskState must be exactly 64 bytes");

class RetailIncomeRiskGovernor {
public:
    static void audit_trade(
        RetailIncomeRiskState& state,
        double equity,
        double free_cash,
        double proposed_collateral,
        double existing_collateral,
        int32_t days_earnings
    ) {
        state.account_equity = equity;
        state.max_symbol_allocation = equity * 0.05;
        state.total_symbol_exposure = existing_collateral + proposed_collateral;
        state.days_to_earnings = days_earnings;

        state.is_symbol_cap_ok = (state.total_symbol_exposure <= state.max_symbol_allocation) ? 1 : 0;
        
        double remaining_cash = free_cash - proposed_collateral;
        state.remaining_cash_buffer_pct = (remaining_cash / std::max(1.0, equity)) * 100.0;
        state.is_cash_buffer_ok = (state.remaining_cash_buffer_pct >= 25.0) ? 1 : 0;

        state.is_earnings_safe = (days_earnings >= 14) ? 1 : 0;
        state.is_trade_approved = (state.is_symbol_cap_ok && state.is_cash_buffer_ok && state.is_earnings_safe) ? 1 : 0;
    }
};

} // namespace optionalpha
