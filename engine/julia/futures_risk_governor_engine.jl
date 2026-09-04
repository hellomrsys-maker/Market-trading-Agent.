# Module AN5 (Julia): Schwager Algorithmic Risk Budgeting & Robust System Optimization Engine
# Precision calculation of ATR position sizing, walk-forward degradation checks, and portfolio heat limits.

module FuturesRiskGovernorEngine

export calculate_atr_position, evaluate_walk_forward

function calculate_atr_position(equity::Float64, risk_pct::Float64, atr::Float64, multiplier::Float64, pt_val::Float64)
    clamped_risk = min(risk_pct, 1.5) / 100.0
    dollar_target = equity * clamped_risk
    per_contract = max(1.0, atr * multiplier * pt_val)
    contracts = max(1, floor(Int, dollar_target / per_contract))
    return (dollar_target = dollar_target, contracts = contracts)
end

function evaluate_walk_forward(is_sharpe::Float64, oos_sharpe::Float64)
    ratio = oos_sharpe / max(1e-4, is_sharpe)
    is_deployable = ratio >= 0.65 && oos_sharpe > 0.5
    return (ratio = ratio, is_deployable = is_deployable)
end

end
