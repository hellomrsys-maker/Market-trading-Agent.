# Module AV5 (Julia): Physical Cash-to-Futures Basis & Storage Arbitrage Engine
# Quantitative basis Z-score analysis and cash-and-carry storage arbitrage calculations.

module CashFuturesBasisArbitrageEngine

export evaluate_basis, evaluate_carry

function evaluate_basis(cash::Float64, futures::Float64, mean::Float64, std_dev::Float64)
    basis = cash - futures
    s = max(1e-4, std_dev)
    z = (basis - mean) / s
    regime = z >= 1.5 ? "STRONG_BASIS" : (z <= -1.5 ? "WEAK_BASIS" : "EQUILIBRIUM")
    return (basis = basis, zscore = z, regime = regime)
end

function evaluate_carry(cash::Float64, futures::Float64, carry_costs::Float64)
    net_profit = (futures - cash) - carry_costs
    profitable = net_profit > 0.0
    return (net_profit = net_profit, is_profitable = profitable)
end

end
