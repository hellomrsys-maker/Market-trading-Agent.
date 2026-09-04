# engine/julia/drawdown_risk_manager.jl
# OptionAlpha Agent — Module T_sys5: Julia Drawdown Risk Manager Engine

module DrawdownRiskManagerJulia

export DrawdownManager, calculate_position_size, update_trade!

mutable struct DrawdownManager
    current_capital::Float64
    peak_equity::Float64
    max_dd_cutoff_pct::Float64
    consecutive_losses::Int
end

function DrawdownManager(initial_capital::Float64=10000.0, max_dd_cutoff_pct::Float64=20.0)
    return DrawdownManager(initial_capital, initial_capital, max_dd_cutoff_pct, 0)
end

function calculate_position_size(dm::DrawdownManager, risk_pct::Float64, max_loss_per_contract::Float64)
    max_dollar_risk = dm.current_capital * (risk_pct / 100.0)
    if max_loss_per_contract <= 0.0
        return 1
    end
    return max(1, floor(Int, max_dollar_risk / max_loss_per_contract))
end

function update_trade!(dm::DrawdownManager, pnl::Float64)
    dm.current_capital += pnl
    if dm.current_capital > dm.peak_equity
        dm.peak_equity = dm.current_capital
    end

    if pnl < 0.0
        dm.consecutive_losses += 1
    else
        dm.consecutive_losses = 0
    end

    dollar_dd = dm.peak_equity - dm.current_capital
    pct_dd = dm.peak_equity > 0.0 ? (dollar_dd / dm.peak_equity) * 100.0 : 0.0
    is_halted = (pct_dd >= dm.max_dd_cutoff_pct) || (dm.consecutive_losses >= 6)

    return (capital=dm.current_capital, pct_dd=pct_dd, is_halted=is_halted)
end

end # module
