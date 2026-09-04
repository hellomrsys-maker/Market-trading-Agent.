# engine/julia/dealer_gamma_simulations.jl
# OptionAlpha Agent — Julia Quantitative Dealer Gamma & Max Pain Simulations
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Distributions
using SpecialFunctions
using Statistics

# Market Maker Map: Max Pain Simulation
# Max Pain reflects minimum dealer payout stress
function simulate_max_pain_surface(strikes::Vector{Float64}, call_oi::Vector{Float64}, put_oi::Vector{Float64})
    n = length(strikes)
    pain_surface = zeros(Float64, n)
    
    Threads.@threads for i in 1:n
        theoretical_settle = strikes[i]
        total_pain = 0.0
        
        for j in 1:n
            strike = strikes[j]
            # Call Pain
            if theoretical_settle > strike
                total_pain += (theoretical_settle - strike) * call_oi[j]
            end
            # Put Pain
            if theoretical_settle < strike
                total_pain += (strike - theoretical_settle) * put_oi[j]
            end
        end
        
        pain_surface[i] = total_pain
    end
    
    min_pain_idx = argmin(pain_surface)
    return (max_pain_strike = strikes[min_pain_idx], pain_profile = pain_surface)
end

# Dealer Gamma Environment: Chop vs Trend
function simulate_dealer_gamma_regime(dealer_net_gamma::Float64, vix_level::Float64, days::Int=30)
    # Long Gamma (Dealers buy dips, sell rallies) -> Mean reversion
    # Short Gamma (Dealers chase price) -> Trending / Expanding vol
    
    paths = zeros(Float64, days)
    paths[1] = 100.0 # Arbitrary base 100
    
    for i in 2:days
        if dealer_net_gamma > 0 && vix_level < 20.0
            # Long Gamma: High mean reversion, low volatility
            noise = randn() * 0.005
            reversion = (100.0 - paths[i-1]) * 0.10
            paths[i] = paths[i-1] + noise + reversion
        else
            # Short Gamma: Trend following, expanding volatility
            noise = randn() * 0.015
            momentum = (paths[i-1] - (i > 2 ? paths[i-2] : 100.0)) * 0.20
            paths[i] = paths[i-1] + noise + momentum
        end
    end
    
    return paths
end
