# Module AJ5 (Julia): Quantitative Mean Reversion, Cointegration & Statistical Arbitrage Engine
# Ornstein-Uhlenbeck stochastic modeling, Hurst exponents, and Z-score statistical arbitrage bounds.

module StatisticalMeanReversionEngine

export evaluate_zscore, calculate_ou_halflife

function evaluate_zscore(current_val::Float64, mean::Float64, std_dev::Float64)
    s = max(1e-5, std_dev)
    z = (current_val - mean) / s
    action = "HOLD"
    if z >= 3.5 || z <= -3.5
        action = "STOP"
    elseif z >= 2.0
        action = "SHORT_SPREAD"
    elseif z <= -2.0
        action = "LONG_SPREAD"
    elseif abs(z) <= 0.5
        action = "TAKE_PROFIT"
    end
    return (z = z, action = action)
end

function calculate_ou_halflife(theta::Float64)
    hl = theta > 0 ? (log(2.0) / theta) : 9999.0
    return hl
end

end
