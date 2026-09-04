# engine/julia/weekly_squeeze_engine.jl
# OptionAlpha Agent — Module Q5: Julia Weekly Squeeze & Heikin Ashi Engine

module WeeklySqueezeEngineJulia

export calculate_heikin_ashi, is_in_squeeze, midpoint_entry

struct HeikinAshiBar
    ha_open::Float64
    ha_high::Float64
    ha_low::Float64
    ha_close::Float64
    is_strong_bull::Bool
    is_strong_bear::Bool
end

function calculate_heikin_ashi(o::Float64, h::Float64, l::Float64, c::Float64, prev_o::Float64, prev_c::Float64)
    ha_open = (prev_o + prev_c) / 2.0
    ha_close = (o + h + l + c) / 4.0
    ha_high = max(h, ha_open, ha_close)
    ha_low = min(l, ha_open, ha_close)
    is_strong_bull = (ha_close > ha_open) && (abs(ha_low - ha_open) < 1e-4)
    is_strong_bear = (ha_close < ha_open) && (abs(ha_high - ha_open) < 1e-4)
    return HeikinAshiBar(ha_open, ha_high, ha_low, ha_close, is_strong_bull, is_strong_bear)
end

function is_in_squeeze(bb_u::Float64, bb_l::Float64, kc_u::Float64, kc_l::Float64)
    return (bb_u < kc_u) && (bb_l > kc_l)
end

function midpoint_entry(o::Float64, c::Float64)
    return (o + c) / 2.0
end

end # module
