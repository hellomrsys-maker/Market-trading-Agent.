# Module AF5 (Julia): Strategic Gamma Scalping & Position Adjustment Engine
# Precision calculation of Gamma Decay Breakeven ("Paying the Rent") and daily sigma moves

module StrategicGammaScalpingEngine

export calculate_gamma_decay_breakeven, calculate_daily_sigma_move

function calculate_gamma_decay_breakeven(daily_theta::Float64, position_gamma::Float64)
    g = max(1e-6, position_gamma)
    th = abs(daily_theta)
    return round(sqrt((2.0 * th) / g), digits=4)
end

function calculate_daily_sigma_move(spot::Float64, annual_vol::Float64)
    daily_vol = annual_vol / sqrt(252.0)
    sigma1 = spot * daily_vol
    return (
        daily_vol_pct = round(daily_vol * 100.0, digits=4),
        one_sigma_move = round(sigma1, digits=2),
        upper_1sigma = round(spot + sigma1, digits=2),
        lower_1sigma = round(spot - sigma1, digits=2)
    )
end

end # module
