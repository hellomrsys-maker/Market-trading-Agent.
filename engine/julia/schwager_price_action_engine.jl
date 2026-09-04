# Module AK5 (Julia): Schwager Classical Price Action & Breakout Trap Engine
# Quantitative detection of key reversal days, island reversals, and spring/upthrust traps.

module SchwagerPriceActionEngine

export evaluate_key_reversal, detect_trap

function evaluate_key_reversal(
    prev_low::Float64, prev_high::Float64, prev_close::Float64,
    curr_low::Float64, curr_high::Float64, curr_close::Float64,
    curr_vol::Float64, avg_vol::Float64
)
    vol_surge = avg_vol <= 0.0 || (curr_vol >= avg_vol * 1.3)
    is_bull = (curr_low < prev_low) && (curr_close > prev_close) && vol_surge
    is_bear = (curr_high > prev_high) && (curr_close < prev_close) && vol_surge

    pattern = is_bull ? "BULLISH_KEY_REVERSAL" : (is_bear ? "BEARISH_KEY_REVERSAL" : "NO_REVERSAL")
    stop_level = is_bull ? curr_low : curr_high

    return (pattern = pattern, is_reversal = is_bull || is_bear, stop_level = stop_level)
end

function detect_trap(support::Float64, resistance::Float64, high::Float64, low::Float64, close::Float64)
    is_spring = (low < support) && (close >= support)
    is_upthrust = (high > resistance) && (close <= resistance)
    trap = is_spring ? "BULLISH_SPRING" : (is_upthrust ? "BEARISH_UPTHRUST" : "NONE")
    return (trap = trap, is_spring = is_spring, is_upthrust = is_upthrust)
end

end
