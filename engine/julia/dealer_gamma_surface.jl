# engine/julia/dealer_gamma_surface.jl
# OptionAlpha Agent — Julia Quantitative Dealer Net Gamma Surface & Flip Dynamics
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Statistics

struct StrikeGammaOI
    strike::Float64
    call_gamma::Float64
    call_oi::Float64
    put_gamma::Float64
    put_oi::Float64
end

function calculate_net_dealer_gex(spot::Float64, strikes_data::Vector{StrikeGammaOI}, multiplier::Float64=100.0)
    total_call_gex = 0.0
    total_put_gex = 0.0
    
    for d in strikes_data
        call_dollar_gex = d.call_gamma * d.call_oi * multiplier * (spot^2) * 0.01 / 1.0e6
        put_dollar_gex = d.put_gamma * d.put_oi * multiplier * (spot^2) * 0.01 / 1.0e6
        total_call_gex += call_dollar_gex
        total_put_gex += put_dollar_gex
    end
    
    net_gex = total_call_gex - total_put_gex
    regime = net_gex >= 0.0 ? :LONG_GAMMA_PINNING : :SHORT_GAMMA_EXPANSION
    
    return (
        net_gex_millions = net_gex,
        regime = regime,
        is_long_gamma = net_gex >= 0.0,
        expected_volatility_behavior = net_gex >= 0.0 ? "Mean-Reversion / Decay" : "Expansion / Momentum"
    )
end
