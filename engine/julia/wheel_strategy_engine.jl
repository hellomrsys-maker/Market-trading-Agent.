# Module AQ5 (Julia): The Wheel Strategy Lifecycle & Dynamic State Machine Engine
# Quantitative lifecycle state transitions and cost-basis amortization calculations.

module WheelStrategyEngine

export track_wheel

function track_wheel(state_id::Int, spot::Float64, cost_basis::Float64, put_prem::Float64, call_prem::Float64, dividends::Float64, strike::Float64, orig_prem::Float64, curr_prem::Float64)
    total_inc = put_prem + call_prem + dividends
    true_basis = cost_basis - total_inc
    profit = orig_prem - curr_prem
    profit_pct = orig_prem > 0 ? (profit / orig_prem) * 100.0 : 0.0
    hit_50 = profit_pct >= 50.0

    return (
        true_cost_basis = true_basis,
        profit_pct = profit_pct,
        is_50pct_hit = hit_50,
        current_state = state_id
    )
end

end
