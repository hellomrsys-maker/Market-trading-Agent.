# Module AA5 (Julia): Tactical Swing Trading & Technical Microstructure Engine
# Quantitative geometry for ABCD patterns, flag momentum formations, and moving average cross modeling.

module TacticalSwingTradingEngine

export evaluate_abcd, detect_flag

function evaluate_abcd(pointA::Float64, pointB::Float64, pointC::Float64, is_bullish::Bool=true)
    ab_leg = abs(pointA - pointB)
    if is_bullish
        pointD = pointC + ab_leg
        stop_loss = pointC * 0.98
        risk = pointC - stop_loss
        rr = risk > 0.0 ? (pointD - pointC) / risk : 0.0
        return (
            pattern = "BULLISH_ABCD",
            point_d_target = round(pointD, digits=2),
            stop_loss = round(stop_loss, digits=2),
            reward_to_risk = round(rr, digits=2)
        )
    else
        pointD = pointC - ab_leg
        stop_loss = pointC * 1.02
        risk = stop_loss - pointC
        rr = risk > 0.0 ? (pointC - pointD) / risk : 0.0
        return (
            pattern = "BEARISH_ABCD",
            point_d_target = round(pointD, digits=2),
            stop_loss = round(stop_loss, digits=2),
            reward_to_risk = round(rr, digits=2)
        )
    end
end

function detect_flag(pole_start::Float64, pole_end::Float64, pullback_extreme::Float64, current_price::Float64)
    pole_height = abs(pole_end - pole_start)
    if pole_height <= 0.0
        return (valid=false, target=0.0)
    end
    pullback_depth = abs(pole_end - pullback_extreme) / pole_height
    if 0.10 <= pullback_depth <= 0.50
        risk = abs(current_price - pullback_extreme)
        target = current_price + 2.0 * risk
        return (valid=true, target=round(target, digits=2), rr=2.0)
    end
    return (valid=false, target=0.0)
end

end # module
