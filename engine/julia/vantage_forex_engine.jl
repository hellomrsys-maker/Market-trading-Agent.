# engine/julia/vantage_forex_engine.jl

function simulate_central_bank_shock(is_hawkish::Bool, current_vol::Float64)
    return is_hawkish ? current_vol * 1.5 : current_vol * 1.2
end
