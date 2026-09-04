# Module BG5 (Julia): Forex Microstructure, Bladerunner 20-EMA & Carry Trade Engine
# Quantitative Bladerunner 20-EMA price action, rollover carry yield, and Kelly sizing in Julia.

module BladerunnerCarryForexEngine

export evaluate_bladerunner, calculate_carry, calculate_kelly

function evaluate_bladerunner(spot::Float64, ema20::Float64, rejected::Bool, confirmed::Bool)
    above = spot > ema20
    polarity = above ? "BULLISH_ABOVE" : "BEARISH_BELOW"
    signal = "WAIT"

    if above && rejected && confirmed
        signal = "ENTER_LONG"
    elseif !above && rejected && confirmed
        signal = "ENTER_SHORT"
    end

    return (polarity = polarity, signal = signal)
end

function calculate_carry(rate_long::Float64, rate_short::Float64, units::Float64)
    diff = (rate_long - rate_short) / 100.0
    daily_int = (diff * units) / 365.0
    return (daily_interest = daily_int, is_positive = daily_int > 0.0)
end

function calculate_kelly(win_prob::Float64, win_loss::Float64)
    w = clamp(win_prob, 0.01, 0.99)
    r = max(0.01, win_loss)
    k = w - ((1.0 - w) / r)
    alloc = clamp(k, 0.0, 0.25)
    return (kelly_fraction = k, allocation_pct = alloc * 100.0)
end

end
