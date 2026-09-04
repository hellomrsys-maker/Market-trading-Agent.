# engine/julia/condor_simulations.jl
# OptionAlpha Agent — Julia Quantitative 4-Leg Iron Condor Probability of Profit (PoP) & Touch PDE
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Distributions
using SpecialFunctions

struct CondorParams
    spot::Float64
    long_put_k::Float64
    short_put_k::Float64
    short_call_k::Float64
    long_call_k::Float64
    T::Float64              # 45 DTE = 45/365
    r::Float64              # 0.05
    sigma::Float64          # IV
    net_credit::Float64
    multiplier::Int         # 100
end

function compute_condor_pop_mc(p::CondorParams, n_paths::Int=50000)
    dt = p.T / 50.0
    drift = (p.r - 0.5 * p.sigma^2) * dt
    vol_step = p.sigma * sqrt(dt)
    
    in_profit_zone = 0
    touched_short_strikes = 0
    terminal_pnls = Float64[]
    
    be_low = p.short_put_k - p.net_credit
    be_high = p.short_call_k + p.net_credit
    
    for _ in 1:n_paths
        st = p.spot
        touched = false
        for _ in 1:50
            st *= exp(drift + vol_step * randn())
            if st <= p.short_put_k || st >= p.short_call_k
                touched = true
            end
        end
        
        if touched
            touched_short_strikes += 1
        end
        
        # Terminal Payoff
        put_spread_loss = max(0.0, p.short_put_k - st) - max(0.0, p.long_put_k - st)
        call_spread_loss = max(0.0, st - p.short_call_k) - max(0.0, st - p.long_call_k)
        total_pnl = (p.net_credit - put_spread_loss - call_spread_loss) * p.multiplier
        push!(terminal_pnls, total_pnl)
        
        if st >= be_low && st <= be_high
            in_profit_zone += 1
        end
    end
    
    return (
        pop_expiration = in_profit_zone / n_paths,
        prob_of_touch = touched_short_strikes / n_paths,
        expected_value_dollars = mean(terminal_pnls),
        sharpe_ratio = mean(terminal_pnls) / std(terminal_pnls)
    )
end
