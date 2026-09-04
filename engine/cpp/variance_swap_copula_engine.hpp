// engine/cpp/variance_swap_copula_engine.hpp
// OptionAlpha Agent — Module X3: C++20 Volatility Derivatives & Copula Zero-Bridge Core
#pragma once

#include "zero_bridge.hpp"
#include <cmath>
#include <algorithm>

namespace optionalpha {

struct alignas(64) VarianceSwapCopulaState {
    double realized_variance;
    double var_swap_cash_gamma;
    double var_swap_vega;
    double var_swap_theta;
    double markowitz_portfolio_var;
    char derivative_tag[19]; // e.g. "VARIANCE_SWAP_LOG"
    char pad[5];             // 64-byte alignment
};

class VarianceSwapCopulaEngineCpp {
public:
    static inline VarianceSwapCopulaState evaluate_variance_greeks_fast(
        double rv, double t_years, double time_elapsed, double sigma, double p_var
    ) {
        double t_rem = std::max(1e-4, t_years - time_elapsed);
        double t_safe = std::max(1e-4, t_years);

        double cash_gamma = 2.0 / t_safe;
        double vega = (2.0 / t_safe) * sigma * t_rem;
        double theta = - (1.0 / t_safe) * sigma * sigma;

        VarianceSwapCopulaState state{};
        state.realized_variance = rv;
        state.var_swap_cash_gamma = cash_gamma;
        state.var_swap_vega = vega;
        state.var_swap_theta = theta;
        state.markowitz_portfolio_var = p_var;
        return state;
    }
};

} // namespace optionalpha
