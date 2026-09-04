# engine/julia/smc_expectancy_engine.jl
# OptionAlpha Agent — Module M5: Julia Kelly Criterion & Multi-Month Expectancy Simulator

function simulate_smc_expectancy(win_rate::Float64, avg_win::Float64, avg_loss::Float64, n_trades::Int)
    expectancy = (win_rate * avg_win) - ((1.0 - win_rate) * avg_loss)
    b = avg_win / avg_loss
    kelly = (b * win_rate - (1.0 - win_rate)) / b
    
    pnl_path = zeros(Float64, n_trades)
    running_r = 0.0
    for i in 1:n_trades
        running_r += (rand() <= win_rate) ? avg_win : -avg_loss
        pnl_path[i] = running_r
    end
    
    return (expectancy = expectancy, half_kelly = max(0.0, kelly / 2.0), total_r = running_r, pnl_path = pnl_path)
end
