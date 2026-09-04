#pragma once
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace optionalpha {

/**
 * 64-byte Zero-Bridge State Vector for Cash-to-Futures Basis & Carry.
 * Exactly 64 bytes with alignas(64).
 */
struct alignas(64) CashFuturesBasisState {
    double local_cash_price;         // 8 bytes
    double front_futures_price;      // 8 bytes
    double current_basis_value;      // 8 bytes
    double basis_zscore;             // 8 bytes
    double carrying_costs;           // 8 bytes
    double net_arbitrage_profit;     // 8 bytes
    uint32_t basis_regime_flag;      // 4 bytes (1 Strong Basis, 2 Weak Basis, 0 Equilibrium)
    uint32_t is_carry_profitable;    // 4 bytes (1 True, 0 False)
    uint8_t padding[8];              // 8 bytes (total = 64 bytes)
};

static_assert(sizeof(CashFuturesBasisState) == 64, "CashFuturesBasisState must be exactly 64 bytes");

class CashFuturesBasisArbitrageEngine {
public:
    static void evaluate_basis(
        CashFuturesBasisState& state,
        double cash,
        double futures,
        double mean,
        double std_dev,
        double carry_costs
    ) {
        state.local_cash_price = cash;
        state.front_futures_price = futures;
        state.current_basis_value = cash - futures;
        
        double s = std::max(1e-4, std_dev);
        state.basis_zscore = (state.current_basis_value - mean) / s;

        if (state.basis_zscore >= 1.5) state.basis_regime_flag = 1; // Strong
        else if (state.basis_zscore <= -1.5) state.basis_regime_flag = 2; // Weak
        else state.basis_regime_flag = 0;

        state.carrying_costs = carry_costs;
        state.net_arbitrage_profit = (futures - cash) - carry_costs;
        state.is_carry_profitable = (state.net_arbitrage_profit > 0.0) ? 1 : 0;
    }
};

} // namespace optionalpha
