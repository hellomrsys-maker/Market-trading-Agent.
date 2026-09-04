# engine/julia/risk_math.jl
# OptionAlpha Agent — Julia Quantitative 99% Delta-Gamma VaR/CVaR, Cornish-Fisher & Macro Stress Testing
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Distributions
using LinearAlgebra

struct PortfolioGreeks
    delta_dollars::Float64
    gamma_dollars::Float64
    vega_dollars::Float64
    theta_dollars::Float64
    portfolio_equity::Float64
end

# 99% 1-Day Delta-Gamma Value-at-Risk (Cornish-Fisher Expansion)
function compute_delta_gamma_var_99(g::PortfolioGreeks, market_vol_1d::Float64=0.012)
    # Delta-Gamma PnL approximation: dV = Delta_$ * dS/S + 0.5 * Gamma_$ * (dS/S)^2
    z_99 = 2.3263 # 99% standard normal quantile
    
    sigma_p = abs(g.delta_dollars) * market_vol_1d
    skewness = (3.0 * sqrt(2.0) * g.gamma_dollars * market_vol_1d^2) / (sigma_p + 1e-6)
    
    # Cornish-Fisher adjusted quantile
    z_cf = z_99 + (skewness / 6.0) * (z_99^2 - 1.0)
    
    var_99_dollars = sigma_p * z_cf + 0.5 * abs(g.gamma_dollars) * (market_vol_1d * z_cf)^2
    var_99_pct = (var_99_dollars / g.portfolio_equity) * 100.0
    cvar_99_dollars = var_99_dollars * 1.15
    
    return (
        var_99_dollars = var_99_dollars,
        var_99_pct = var_99_pct,
        cvar_99_dollars = cvar_99_dollars,
        is_compliant = var_99_pct <= 3.0 # Strict <3% daily capital risk limit
    )
end

# CCAR Institutional Macro Stress Scenarios
function evaluate_macro_stress_tests(g::PortfolioGreeks)
    scenarios = Dict(
        "Flash_Crash_Minus_10pct" => (-0.10, 0.50), # -10% spot, +50% vol spike
        "Vol_Crush_Plus_5pct"     => ( 0.05, -0.30), # +5% spot, -30% vol crush
        "Gap_Up_Plus_8pct"        => ( 0.08, -0.15), # +8% spot, -15% vol
        "Liquidity_Freeze_Stag"   => ( 0.00, 0.40)   # 0% spot, +40% vol freeze
    )
    
    results = Dict{String, Float64}()
    for (name, (ds, dvol)) in scenarios
        # dV = Delta_$ * ds + 0.5 * Gamma_$ * ds^2 + Vega_$ * dvol * 100 + Theta_$
        pnl = g.delta_dollars * ds + 0.5 * g.gamma_dollars * (ds^2) + g.vega_dollars * (dvol * 100.0) + g.theta_dollars
        results[name] = pnl
    end
    return results
end
