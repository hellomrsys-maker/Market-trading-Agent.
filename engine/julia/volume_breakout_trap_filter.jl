# Module BC5 (Julia): Volume Spread Analysis & False Breakout / Trap Filter Engine
# Quantitative volume surge validation and Wyckoff trap identification.

module VolumeBreakoutTrapFilter

export evaluate_volume, detect_trap

function evaluate_volume(vol::Float64, sma_vol::Float64, candle_closed::Bool)
    surge = vol / max(1.0, sma_vol)
    confirmed = surge >= 1.50 && candle_closed
    return (surge_ratio = surge, is_confirmed = confirmed)
end

function detect_trap(key_level::Float64, extreme_px::Float64, close_px::Float64, is_support::Bool)
    is_trap = is_support ? (extreme_px < key_level && close_px >= key_level) : (extreme_px > key_level && close_px <= key_level)
    action = is_trap ? "FADE_FALSE_BREAK" : "FOLLOW_TREND"
    return (is_trap = is_trap, action = action)
end

end
