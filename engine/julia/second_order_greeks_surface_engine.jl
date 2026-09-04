# Module AD5 (Julia): Higher-Order Greeks, Moments & Volatility Surface Engine
# Quantitative evaluation of Forward Implied Volatility and Greek surface behaviors

module SecondOrderGreeksSurfaceEngine

export calculate_forward_vol, evaluate_term_structure

function calculate_forward_vol(vol1::Float64, days1::Int, vol2::Float64, days2::Int)
    if days2 <= days1
        return vol2
    end
    v1_sq_t = (vol1^2) * Float64(days1)
    v2_sq_t = (vol2^2) * Float64(days2)
    dt = Float64(days2 - days1)
    num = v2_sq_t - v1_sq_t
    return num > 0.0 ? round(sqrt(num / dt), digits=4) : 0.0
end

function evaluate_term_structure(days_near::Int, vol_near::Float64, days_far::Int, vol_far::Float64)
    slope = (vol_far - vol_near) / Float64(days_far - days_near)
    regime = slope > 0.0005 ? "NORMAL_CONTANGO" : (slope < -0.0005 ? "INVERTED_BACKWARDATION" : "FLAT")
    return (
        regime = regime,
        slope = round(slope, digits=6)
    )
end

end # module
