# Module AC5 (Julia): Options Equivalency, Synthetics & Arbitrage Engine
# Scientific evaluation of Put-Call parity, forward carry, and box spread arbitrage

module OptionsEquivalencyEngine

export compute_basis, evaluate_parity, evaluate_box

function compute_basis(stock::Float64, rate::Float64, days::Int, div::Float64=0.0)
    t = Float64(days) / 360.0
    carry = stock * rate * t
    basis = carry - div
    fwd = stock + basis
    return (carry=round(carry, digits=4), basis=round(basis, digits=4), forward_price=round(fwd, digits=4))
end

function evaluate_parity(stock::Float64, strike::Float64, call::Float64, put::Float64, rate::Float64, days::Int, div::Float64=0.0)
    t = Float64(days) / 360.0
    basis = (stock * rate * t) - div
    theo_stock = call - put + strike - basis
    synth_call = stock - strike + put + basis
    synth_put = call + strike - stock - basis
    return (
        actual_stock = stock,
        theoretical_stock = round(theo_stock, digits=4),
        synthetic_call = round(synth_call, digits=4),
        synthetic_put = round(synth_put, digits=4)
    )
end

function evaluate_box(call_vert::Float64, put_vert::Float64, k1::Float64, k2::Float64)
    cost = call_vert + put_vert
    par = abs(k2 - k1)
    profit = par - cost
    return (
        box_cost = round(cost, digits=4),
        par_value = round(par, digits=4),
        profit = round(profit, digits=4),
        is_arbitrage = profit > 0.05
    )
end

end # module
