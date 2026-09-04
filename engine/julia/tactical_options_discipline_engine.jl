# Module AB5 (Julia): Tactical Options Structuring & Execution Discipline Engine
# High-precision options payoff modeling, Iron Condor wing insurance analysis, and capital sizing rules.

module TacticalOptionsDisciplineEngine

export calculate_position_size, structure_iron_condor

function calculate_position_size(equity::Float64, entry::Float64, stop::Float64, is_aggressive::Bool=false)
    risk_frac = is_aggressive ? 0.02 : 0.01
    dollar_risk = equity * risk_frac
    per_share_risk = abs(entry - stop)
    shares = per_share_risk > 0.0 ? floor(Int, dollar_risk / per_share_risk) : 0
    contracts = floor(Int, shares / 100)
    return (
        dollar_risk = round(dollar_risk, digits=2),
        shares = shares,
        contracts = contracts
    )
end

function structure_iron_condor(k1::Float64, k2::Float64, k3::Float64, k4::Float64,
                               p_short::Float64, p_long::Float64, c_short::Float64, c_long::Float64)
    put_credit = p_short - p_long
    call_credit = c_short - c_long
    total_credit = (put_credit + call_credit) * 100.0
    wing_width = (k2 - k1) * 100.0
    max_loss = max(0.0, wing_width - total_credit)
    rr = max_loss > 0.0 ? total_credit / max_loss : 0.0
    
    return (
        net_credit = round(total_credit, digits=2),
        wing_width = round(wing_width, digits=2),
        max_loss = round(max_loss, digits=2),
        reward_to_risk = round(rr, digits=2)
    )
end

end # module
