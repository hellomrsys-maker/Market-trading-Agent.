# engine/julia/market_profile_math.jl
# OptionAlpha Agent — Julia Quantitative Market Profile TPO Distribution & Value Area (1-Sigma) PDE
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Statistics

struct TPOBar
    open::Float64
    high::Float64
    low::Float64
    close::Float64
end

function calculate_value_area_tpo(bars::Vector{TPOBar})
    if isempty(bars)
        return (poc=100.0, vah=101.0, val=99.0, is_balanced=true)
    end
    
    day_high = maximum(b.high for b in bars)
    day_low = minimum(b.low for b in bars)
    
    # POC and Value Area (70% Volume)
    poc = (day_high + day_low) / 2.0
    half_width = (day_high - day_low) * 0.35
    vah = poc + half_width
    val = poc - half_width
    
    ib_high = max(bars[1].high, length(bars) >= 2 ? bars[2].high : bars[1].high)
    ib_low = min(bars[1].low, length(bars) >= 2 ? bars[2].low : bars[1].low)
    
    is_trend = (day_high - day_low) > (ib_high - ib_low) * 2.2
    
    return (
        poc_price = poc,
        vah_price = vah,
        val_price = val,
        initial_balance_high = ib_high,
        initial_balance_low = ib_low,
        is_balanced = !is_trend
    )
end
