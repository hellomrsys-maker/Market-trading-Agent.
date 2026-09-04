# engine/julia/cognitive_bias_auditor_engine.jl
# OptionAlpha Agent — Module P5: Julia Behavioral Drawdown & Bias Impact Simulator

function simulate_bias_impact(unbiased_expectancy::Float64, rule_violation_rate::Float64, n_trades::Int)
    # Simulates performance degradation when psychological biases (FOMO, Revenge) are present
    pnl = zeros(Float64, n_trades)
    running_r = 0.0
    for i in 1:n_trades
        is_violation = rand() <= rule_violation_rate
        trade_r = is_violation ? -1.0 : ((rand() <= 0.55) ? 1.8 : -1.0)
        running_r += trade_r
        pnl[i] = running_r
    end
    return (final_r = running_r, pnl_trajectory = pnl)
end
