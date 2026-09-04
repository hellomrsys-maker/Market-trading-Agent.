# engine/julia/option_buying_rules_engine.jl
# OptionAlpha Agent — Module J5: Julia Option Buying Gamma/Theta & Volatility Pricing Simulator

function simulate_theta_vs_gamma(spot::Float64, strike::Float64, days_to_expiry::Int, vol::Float64)
    # Simulates ITM Option Buyer PnL progression considering accelerating Theta decay vs Gamma expansion
    decay_curve = zeros(Float64, days_to_expiry)
    for t in 1:days_to_expiry
        theta_decay = (vol * spot / (2.0 * sqrt(max(0.1, (days_to_expiry - t + 1) / 365.0)))) * 0.01
        decay_curve[t] = theta_decay
    end
    return decay_curve
end
