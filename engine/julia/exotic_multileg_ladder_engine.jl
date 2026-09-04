module ExoticMultiLegLadderEngineModule

export ExoticMultiLegLadderState, construct_strip, construct_strap

struct ExoticMultiLegLadderState
    strike_rung1::Float64
    strike_rung2::Float64
    strike_rung3::Float64
    lambda_elasticity::Float64
    net_package_premium::Float64
    strategy_archetype::Int32
end

function construct_strip(spot::Float64, atm::Float64, call_prem::Float64, put_prem::Float64)::ExoticMultiLegLadderState
    tot = (2.0 * put_prem) + call_prem
    delta = (1.0 * 0.50) + (2.0 * (-0.50))
    lam = tot > 0.001 ? (delta * spot) / tot : 0.0
    return ExoticMultiLegLadderState(atm, atm, atm, lam, tot, 1)
end

function construct_strap(spot::Float64, atm::Float64, call_prem::Float64, put_prem::Float64)::ExoticMultiLegLadderState
    tot = (2.0 * call_prem) + put_prem
    delta = (2.0 * 0.50) + (1.0 * (-0.50))
    lam = tot > 0.001 ? (delta * spot) / tot : 0.0
    return ExoticMultiLegLadderState(atm, atm, atm, lam, tot, 2)
end

end
