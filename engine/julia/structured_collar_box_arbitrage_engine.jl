# Module BH5 (Julia): Structured Options, Collars & Binary Box Arbitrage Engine
# Quantitative costless collars, Long Box risk-free arbitrage, and binary fixed return payouts in Julia.

module StructuredCollarBoxArbitrageEngine

export structure_collar, evaluate_box, evaluate_binary

function structure_collar(basis::Float64, call_k::Float64, call_prem::Float64, put_k::Float64, put_prem::Float64)
    net_collar = call_prem - put_prem
    is_costless = net_collar >= 0.0
    max_up = (call_k - basis) + net_collar
    max_down = (basis - put_k) - net_collar
    return (net_collar = net_collar, is_costless = is_costless, max_up = max_up, max_down = max_down)
end

function evaluate_box(k1::Float64, k2::Float64, debit::Float64)
    payoff = k2 - k1
    profit = payoff - debit
    return (risk_free_profit = profit, is_profitable = profit > 0.0)
end

function evaluate_binary(bet::Float64, payout_pct::Float64, rebate_pct::Float64, itm::Bool)
    total_return = itm ? bet * (1.0 + payout_pct / 100.0) : bet * (rebate_pct / 100.0)
    net_profit = total_return - bet
    return (total_return = total_return, net_profit = net_profit)
end

end
