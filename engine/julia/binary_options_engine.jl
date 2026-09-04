# engine/julia/binary_options_engine.jl
# OptionAlpha Agent — Module S5: Julia Binary Options & Volatility Strangle Engine

module BinaryOptionsEngineJulia

export calculate_binary_collateral, price_short_volatility_strangle

function calculate_binary_collateral(is_long::Bool, premium::Float64, contracts::Int=1)
    collateral = is_long ? premium * contracts : (100.0 - premium) * contracts
    max_profit = is_long ? (100.0 - premium) * contracts : premium * contracts
    rr_ratio = max_profit / max(1e-4, collateral)
    return (collateral=collateral, max_profit=max_profit, rr_ratio=rr_ratio)
end

function price_short_volatility_strangle(high_ask::Float64, low_bid::Float64, contracts::Int=1)
    long_cost = low_bid
    short_collateral = 100.0 - high_ask
    total_collateral = (long_cost + short_collateral) * contracts
    max_profit = (200.0 * contracts) - total_collateral

    upper_loss = short_collateral - (100.0 - long_cost)
    lower_loss = long_cost - (100.0 - short_collateral)
    max_loss = max(abs(upper_loss), abs(lower_loss)) * contracts

    return (total_collateral=total_collateral, max_profit=max_profit, max_loss=max_loss)
end

end # module
