# engine/julia/order_flow_footprint_engine.jl
# OptionAlpha Agent — Module I5: Julia Order Flow Footprint & Delta Divergence Modeling

using Statistics

function compute_value_area_profile(price_levels::Vector{Float64}, volume_nodes::Vector{Float64})
    total_volume = sum(volume_nodes)
    target_70pct = 0.70 * total_volume
    
    vpoc_idx = argmax(volume_nodes)
    vpoc = price_levels[vpoc_idx]
    
    sorted_indices = sortperm(volume_nodes, rev=true)
    accumulated_vol = 0.0
    va_levels = Float64[]
    
    for idx in sorted_indices
        accumulated_vol += volume_nodes[idx]
        push!(va_levels, price_levels[idx])
        if accumulated_vol >= target_70pct
            break
        end
    end
    
    vah = maximum(va_levels)
    val = minimum(va_levels)
    
    return (vpoc = vpoc, vah = vah, val = val, total_volume = total_volume)
end

function simulate_delta_exhaustion(prices::Vector{Float64}, deltas::Vector{Float64})
    n = length(prices)
    divergence_signals = zeros(Int32, n)
    for i in 2:n
        price_diff = prices[i] - prices[i-1]
        delta_diff = deltas[i] - deltas[i-1]
        if price_diff > 0 && delta_diff < 0
            divergence_signals[i] = -1 # Bearish Exhaustion Divergence
        elseif price_diff < 0 && delta_diff > 0
            divergence_signals[i] = 1  # Bullish Absorption Divergence
        end
    end
    return divergence_signals
end
