# engine/julia/cliquet_mountain_range_engine.jl
# OptionAlpha Agent — Module W5: Julia Cliquet, Napoleon & Mountain Range Engine

module CliquetMountainRangeEngineJulia

export calculate_lflc_cliquet, calculate_gflc_cliquet, calculate_napoleon, calculate_everest

function calculate_lflc_cliquet(returns::Vector{Float64}, local_floor::Float64, local_cap::Float64)
    return sum(max.(local_floor, min.(returns, local_cap)))
end

function calculate_gflc_cliquet(returns::Vector{Float64}, local_floor::Float64, local_cap::Float64, global_floor::Float64, global_cap::Float64)
    raw = calculate_lflc_cliquet(returns, local_floor, local_cap)
    return max(global_floor, min(global_cap, raw))
end

function calculate_napoleon(returns::Vector{Float64}, max_coupon::Float64)
    worst = minimum(returns)
    return max(0.0, max_coupon + worst)
end

function calculate_everest(returns::Vector{Float64}, coupon::Float64)
    worst = minimum(returns)
    return coupon + worst
end

end # module
