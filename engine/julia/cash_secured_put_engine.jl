# Module AO5 (Julia): Cash-Secured Put (CSP) Ladder & Acquisition Basis Optimizer Engine
# Quantitative evaluation of CSP discount basis, ROC %, and POP statistics.

module CashSecuredPutEngine

export evaluate_csp

function evaluate_csp(spot::Float64, strike::Float64, premium::Float64, dte::Float64, delta::Float64)
    basis = strike - premium
    discount_pct = ((spot - basis) / spot) * 100.0
    collateral = strike * 100.0
    trade_roc = (premium * 100.0 / collateral) * 100.0
    ann_roc = trade_roc * (365.0 / max(1.0, dte))
    abs_d = abs(delta)
    pop = (1.0 - abs_d) * 100.0
    is_optimal = (abs_d >= 0.20 && abs_d <= 0.30) && (dte >= 30.0 && dte <= 45.0)

    return (
        effective_basis = basis,
        discount_pct = discount_pct,
        annualized_roc = ann_roc,
        pop = pop,
        is_optimal = is_optimal
    )
end

end
