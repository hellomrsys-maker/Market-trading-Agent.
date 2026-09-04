# engine/julia/forex_math.jl
# OptionAlpha Agent — Julia Quantitative Forex Pip Valuation & Margin Sizing Engine
# Polyglot Pillar 2: Julia Quantitative Mathematics

using Statistics

function calculate_forex_pip_usd(pair::String, units::Int, spot::Float64)
    is_jpy = occursin("JPY", uppercase(pair))
    pip_scale = is_jpy ? 0.01 : 0.0001
    
    if endswith(uppercase(pair), "USD")
        return pip_scale * units
    elseif startswith(uppercase(pair), "USD")
        return (pip_scale * units) / max(1e-4, spot)
    else
        return pip_scale * units
    end
end

function calculate_forex_position_size(pair::String, equity::Float64, risk_pct::Float64, stop_pips::Float64, spot::Float64, leverage::Float64=100.0)
    safe_risk = clamp(risk_pct, 0.005, 0.02)
    risk_dollars = equity * safe_risk
    
    pip_1_lot = calculate_forex_pip_usd(pair, 100000, spot)
    dollar_risk_lot = stop_pips * pip_1_lot
    
    lots = max(0.01, risk_dollars / dollar_risk_lot)
    units = round(Int, lots * 100000)
    pip_val = calculate_forex_pip_usd(pair, units, spot)
    margin = (units * spot) / leverage
    
    return (
        lots = lots,
        units = units,
        pip_value_usd = pip_val,
        risk_dollars = risk_dollars,
        margin_required_usd = margin
    )
end
