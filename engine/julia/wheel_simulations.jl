# engine/julia/wheel_simulations.jl
# OptionAlpha Agent — Julia Quantitative Wheel Strategy (CSP + Covered Call) Monte Carlo Simulation
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Distributions
using SpecialFunctions

struct WheelParams
    initial_equity::Float64
    spot::Float64
    mu::Float64             # Expected underlying return (drift)
    sigma::Float64          # Realized volatility
    iv_premium_spread::Float64 # Implied vs Realized variance risk premium
    n_days::Int             # 252 days = 1 year
    multiplier::Int         # 100 shares per contract
end

function simulate_wheel_lifecycle_mc(p::WheelParams, n_paths::Int=20000)
    dt = 1.0 / 252.0
    drift_step = (p.mu - 0.5 * p.sigma^2) * dt
    vol_step = p.sigma * sqrt(dt)
    
    cagr_results = Float64[]
    max_drawdowns = Float64[]
    assignments_count = Int[]
    
    for _ in 1:n_paths
        equity = p.initial_equity
        spot = p.spot
        holding_stock = false
        stock_basis = 0.0
        n_assignments = 0
        peak_equity = equity
        max_dd = 0.0
        
        day = 1
        while day <= p.n_days
            if !holding_stock
                # Phase 1: Sell 30-DTE OTM Cash-Secured Put (Delta ~ 0.30)
                strike = round((spot * 0.95) / 2.5) * 2.5
                iv = p.sigma + p.iv_premium_spread
                put_prem = spot * 0.018 * p.multiplier
                equity += put_prem
                
                # Evolve 30 days
                for _ in 1:min(30, p.n_days - day + 1)
                    spot *= exp(drift_step + vol_step * randn())
                    day += 1
                end
                
                if spot < strike
                    # Assigned stock
                    holding_stock = true
                    stock_basis = strike
                    n_assignments += 1
                end
            else
                # Phase 2: Sell 30-DTE OTM Covered Call (Delta ~ 0.20)
                strike = max(round((spot * 1.05) / 2.5) * 2.5, stock_basis)
                call_prem = spot * 0.015 * p.multiplier
                equity += call_prem
                
                for _ in 1:min(30, p.n_days - day + 1)
                    spot *= exp(drift_step + vol_step * randn())
                    day += 1
                end
                
                if spot >= strike
                    # Called away at profit
                    equity += (strike - stock_basis) * p.multiplier
                    holding_stock = false
                end
            end
            
            # Track peak equity & drawdown
            current_portfolio = equity + (holding_stock ? (spot - stock_basis) * p.multiplier : 0.0)
            if current_portfolio > peak_equity
                peak_equity = current_portfolio
            else
                dd = (peak_equity - current_portfolio) / peak_equity
                if dd > max_dd
                    max_dd = dd
                end
            end
        end
        
        final_equity = equity + (holding_stock ? (spot - stock_basis) * p.multiplier : 0.0)
        cagr = (final_equity / p.initial_equity) - 1.0
        push!(cagr_results, cagr)
        push!(max_drawdowns, max_dd)
        push!(assignments_count, n_assignments)
    end
    
    return (
        mean_cagr = mean(cagr_results),
        median_cagr = median(cagr_results),
        sharpe_ratio = mean(cagr_results) / std(cagr_results),
        max_drawdown_95th = quantile(max_drawdowns, 0.95),
        avg_annual_assignments = mean(assignments_count)
    )
end
