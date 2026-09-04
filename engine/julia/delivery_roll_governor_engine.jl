# Module AT5 (Julia): Commodity Physical Delivery Risk, First Notice Day (FND) & Roll Governor Engine
# Quantitative modeling of delivery risk deadlines and volume crossover thresholds.

module DeliveryRollGovernorEngine

export evaluate_roll

function evaluate_roll(is_physical::Bool, days_fnd::Int, vol_m1::Float64, vol_m2::Float64)
    vol_cross = vol_m2 > vol_m1
    fnd_danger = is_physical && days_fnd <= 5
    action = (is_physical && days_fnd <= 1) ? "LIQUIDATE" : ((fnd_danger || vol_cross) ? "ROLL" : "HOLD")
    
    return (
        is_physical = is_physical,
        vol_crossover = vol_cross,
        fnd_danger = fnd_danger,
        action = action
    )
end

end
