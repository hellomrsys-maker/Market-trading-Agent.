# engine/julia/provest_math.jl
# OptionAlpha Agent — Julia Quantitative PROVEST Framework & Decile Volatility Ranking Engine
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Distributions
using Statistics

struct PROVESTCriteria
    symbol::String
    current_iv::Float64
    iv_history_24m::Vector{Float64}
    rv_20d::Float64
    directional_bias::Symbol # :BULLISH, :BEARISH, :NEUTRAL
end

function compute_provest_decile(history::Vector{Float64}, current_iv::Float64)
    if isempty(history)
        return 5
    end
    sorted_hist = sort(history)
    count_below = count(x -> x <= current_iv, sorted_hist)
    percentile = count_below / length(sorted_hist)
    decile = ceil(Int, percentile * 10.0)
    return clamp(decile, 1, 10)
end

function evaluate_provest_matrix(c::PROVESTCriteria)
    rank = compute_provest_decile(c.iv_history_24m, c.current_iv)
    vrp = c.current_iv - c.rv_20d
    
    # Strategy Matrix
    selected_strategy = if c.directional_bias == :BULLISH
        rank <= 4 ? "LONG_CALL_DEEP_ITM" : "BULL_PUT_SPREAD"
    elseif c.directional_bias == :BEARISH
        rank <= 4 ? "LONG_PUT_DEEP_ITM" : "BEAR_CALL_SPREAD"
    else
        rank <= 3 ? "CALENDAR_SPREAD" : (rank >= 7 ? "IRON_CONDOR" : "WHEEL_CSP")
    end
    
    return (
        relative_vol_rank = rank,
        vrp = vrp,
        target_strategy = selected_strategy,
        is_option_writing_favorable = rank >= 6,
        is_option_buying_favorable = rank <= 4
    )
end
