# Module AH5 (Julia): Dynamic Algorithmic Gamma Scalping & Discrete Rebalancing Engine
# Asymptotic Leland-Whalley-Wilmott rebalancing threshold optimization and scalping PnL simulation.

module DynamicGammaScalpingEngine

export compute_band, calculate_scalp_pnl

function compute_band(portfolio_gamma::Float64, cost::Float64, risk_aversion::Float64)
    abs_g = max(1e-7, abs(portfolio_gamma))
    term = (1.5 * cost * abs_g) / max(1e-5, risk_aversion)
    threshold = clamp(cbrt(term), 0.02, 0.25)
    return threshold
end

function calculate_scalp_pnl(gamma::Float64, spot::Float64, real_vol::Float64, imp_vol::Float64, dt_years::Float64, costs::Float64)
    gamma_dollar = 0.5 * gamma * (spot^2)
    var_diff = (real_vol^2) - (imp_vol^2)
    gross_pnl = gamma_dollar * var_diff * dt_years
    net_pnl = gross_pnl - costs
    return (gross_pnl = gross_pnl, net_pnl = net_pnl, is_profitable = net_pnl > 0)
end

end
