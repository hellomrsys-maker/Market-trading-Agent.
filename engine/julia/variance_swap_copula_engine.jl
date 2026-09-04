# engine/julia/variance_swap_copula_engine.jl
# OptionAlpha Agent — Module X5: Julia Volatility Derivatives & Copula Engine

module VarianceSwapCopulaEngineJulia

export calculate_realized_variance, calculate_variance_swap_greeks

function calculate_realized_variance(log_returns::Vector{Float64}, annualization_factor::Float64=252.0)
    if isempty(log_returns)
        return 0.0
    end
    sum_sq = sum(log_returns .^ 2)
    return (annualization_factor / length(log_returns)) * sum_sq
end

function calculate_variance_swap_greeks(t_years::Float64, time_elapsed::Float64, current_sigma::Float64)
    t_rem = max(1e-4, t_years - time_elapsed)
    t_safe = max(1e-4, t_years)

    cash_gamma = 2.0 / t_safe
    vega = (2.0 / t_safe) * current_sigma * t_rem
    theta = - (1.0 / t_safe) * current_sigma * current_sigma

    return (cash_gamma=cash_gamma, vega=vega, theta=theta)
end

end # module
