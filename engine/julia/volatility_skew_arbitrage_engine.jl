# Module AY5 (Julia): Volatility Skew, Smile Geometry & Ratio Arbitrage Engine
# Quantitative strike skew slopes, term structure slopes, and Broken Wing Butterfly structures.

module VolatilitySkewArbitrageEngine

export evaluate_skew, structure_bwb

function evaluate_skew(iv_atm::Float64, iv_put25::Float64, iv_call25::Float64, iv_30::Float64, iv_90::Float64)
    strike_skew = (iv_put25 - iv_call25) / max(1e-4, iv_atm)
    term_slope = (iv_90 - iv_30) / max(1e-4, iv_30)
    is_steep = strike_skew >= 0.25
    return (strike_skew = strike_skew, term_slope = term_slope, is_steep = is_steep)
end

function structure_bwb(k1::Float64, k2::Float64, k3::Float64, c1::Float64, c2::Float64, c3::Float64)
    net_credit = (2.0 * c2) - c1 - c3
    max_profit = (k2 - k1) + net_credit
    zero_risk = net_credit >= 0.0
    return (net_credit = net_credit, max_profit = max_profit, has_zero_downside_risk = zero_risk)
end

end
