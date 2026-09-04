# Module AE5 (Julia): Multi-Dimensional Spread, Ratio & Wing Engine
# Modeling ratio spreads, backspreads, and butterfly structures in Julia

module MultidimensionalSpreadWingEngine

export structure_ratio_spread, structure_backspread

function structure_ratio_spread(k1::Float64, k2::Float64, prem_long::Float64, prem_short::Float64)
    net_cash = (2.0 * prem_short) - prem_long
    strike_diff = k2 - k1
    max_profit = strike_diff + net_cash
    upside_be = k2 + max_profit
    escape_strike = k2 + strike_diff

    return (
        spread_type = "CALL_RATIO_1X2",
        net_cash = round(net_cash, digits=2),
        max_profit = round(max_profit, digits=2),
        upside_breakeven = round(upside_be, digits=2),
        butterfly_escape_strike = escape_strike
    )
end

function structure_backspread(k1::Float64, k2::Float64, prem_short::Float64, prem_long::Float64)
    net_credit = prem_short - (2.0 * prem_long)
    strike_diff = k2 - k1
    max_loss = max(0.0, strike_diff - net_credit)
    upside_be = k2 + strike_diff - net_credit

    return (
        spread_type = "CALL_BACKSPREAD_2X1",
        net_credit = round(net_credit, digits=2),
        max_loss = round(max_loss, digits=2),
        upside_breakeven = round(upside_be, digits=2)
    )
end

end # module
