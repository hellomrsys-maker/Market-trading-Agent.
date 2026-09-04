# engine/julia/butterfly_simulations.jl
# OptionAlpha Agent — Julia Quantitative Iron Butterfly Pinning & Volatility Crush Simulations
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Distributions
using SpecialFunctions

struct ButterflyParams
    spot::Float64
    center_k::Float64
    wing_width::Float64
    T::Float64
    r::Float64
    sigma::Float64
    net_credit::Float64
    multiplier::Int
end

function simulate_butterfly_payoff_mc(p::ButterflyParams, n_paths::Int=50000)
    dt = p.T / 50.0
    drift = (p.r - 0.5 * p.sigma^2) * dt
    vol_step = p.sigma * sqrt(dt)
    
    payoffs = Float64[]
    in_pin_zone = 0
    
    for _ in 1:n_paths
        st = p.spot
        for _ in 1:50
            st *= exp(drift + vol_step * randn())
        end
        
        # Payoff calculation
        call_spread = max(0.0, st - p.center_k) - max(0.0, st - (p.center_k + p.wing_width))
        put_spread = max(0.0, p.center_k - st) - max(0.0, (p.center_k - p.wing_width) - st)
        pnl = (p.net_credit - call_spread - put_spread) * p.multiplier
        push!(payoffs, pnl)
        
        if abs(st - p.center_k) <= p.net_credit
            in_pin_zone += 1
        end
    end
    
    return (
        pin_probability = in_pin_zone / n_paths,
        expected_value_dollars = mean(payoffs),
        max_possible_return = p.net_credit * p.multiplier,
        max_possible_loss = (p.wing_width - p.net_credit) * p.multiplier
    )
end
