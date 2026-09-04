# engine/julia/dispersion_rainbow_engine.jl
# OptionAlpha Agent — Module U5: Julia Dispersion, Rainbow & Basket Engine

module DispersionRainbowEngineJulia

export calculate_basket_variance, calculate_rainbow_payoff, evaluate_icbc_vs_cbc

function calculate_basket_variance(weights::Vector{Float64}, vols::Vector{Float64}, corr::Matrix{Float64})
    cov = (vols * vols') .* corr
    return max(1e-6, weights' * cov * weights)
end

function calculate_rainbow_payoff(returns::Vector{Float64}, weights_desc::Vector{Float64})
    sorted = sort(returns, rev=true)
    n = min(length(sorted), length(weights_desc))
    return max(0.0, sum(weights_desc[1:n] .* sorted[1:n]))
end

function evaluate_icbc_vs_cbc(rets::Vector{Float64}, cap::Float64)
    n = length(rets)
    icbc = max(0.0, sum(min.(rets, cap)) / n)
    cbc = max(0.0, min(sum(rets) / n, cap))
    return (icbc=icbc, cbc=cbc, dispersion_benefit=cbc - icbc)
end

end # module
