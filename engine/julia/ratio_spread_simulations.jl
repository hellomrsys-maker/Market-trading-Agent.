# engine/julia/ratio_spread_simulations.jl
# OptionAlpha Agent — Julia Quantitative Put Ratio Spread (1x2) Volatility Skew Arbitrage
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Distributions

struct RatioSpreadParams
    spot::Float64
    long_k::Float64
    short_k::Float64
    T::Float64
    r::Float64
    sigma::Float64
    net_credit::Float64
    multiplier::Int
end

function simulate_put_ratio_spread_payoff_mc(p::RatioSpreadParams, n_paths::Int=50000)
    dt = p.T / 50.0
    drift = (p.r - 0.5 * p.sigma^2) * dt
    vol_step = p.sigma * sqrt(dt)
    
    payoffs = Float64[]
    be_lower = p.short_k - (p.long_k - p.short_k) - p.net_credit
    
    for _ in 1:n_paths
        st = p.spot
        for _ in 1:50
            st *= exp(drift + vol_step * randn())
        end
        
        # 1 Long Put + 2 Short Puts Payoff
        long_put_pnl = max(0.0, p.long_k - st)
        short_put_pnl = 2.0 * max(0.0, p.short_k - st)
        total_pnl = (p.net_credit + long_put_pnl - short_put_pnl) * p.multiplier
        push!(payoffs, total_pnl)
    end
    
    return (
        expected_value_dollars = mean(payoffs),
        max_profit_dollars = ((p.long_k - p.short_k) + p.net_credit) * p.multiplier,
        breakeven_lower = be_lower,
        tail_loss_99th = quantile(payoffs, 0.01)
    )
end
