# Module BB5 (Julia): Bilateral & Continuation Geometric Pattern Engine
# Quantitative evaluation of triangle compressions, flags, and continuation projections.

module ContinuationGeometryPatternEngine

export evaluate_triangle, evaluate_flag

function evaluate_triangle(upper_slope::Float64, lower_slope::Float64, base_height::Float64, breakout_px::Float64, spot::Float64)
    if abs(upper_slope) < 0.05 && lower_slope > 0.05
        type_str = "ASCENDING_TRIANGLE"
        target = breakout_px + base_height
        breakout = spot > breakout_px
    elseif abs(lower_slope) < 0.05 && upper_slope < -0.05
        type_str = "DESCENDING_TRIANGLE"
        target = breakout_px - base_height
        breakout = spot < breakout_px
    else
        type_str = "SYMMETRICAL_TRIANGLE"
        target = spot > breakout_px ? (breakout_px + base_height) : (breakout_px - base_height)
        breakout = abs(spot - breakout_px) > 0.5
    end

    return (pattern_type = type_str, target = target, is_breakout = breakout)
end

function evaluate_flag(flag_start::Float64, flag_peak::Float64, breakout_px::Float64, spot::Float64, is_bull::Bool)
    height = abs(flag_peak - flag_start)
    target = is_bull ? (breakout_px + height) : (breakout_px - height)
    breakout = is_bull ? (spot > breakout_px) : (spot < breakout_px)
    return (height = height, target = target, is_breakout = breakout)
end

end
