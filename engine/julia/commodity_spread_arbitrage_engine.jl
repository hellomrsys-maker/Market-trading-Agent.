# Module AL5 (Julia): Intermarket Commodity Processing & Calendar Spread Arbitrage Engine
# Quantitative modeling of 3:2:1 energy cracks, soybean crush margins, and cost-of-carry.

module CommoditySpreadArbitrageEngine

export compute_crack_321, compute_soybean_crush

function compute_crack_321(cl::Float64, rbob::Float64, ho::Float64)
    gas_bbl = rbob * 42.0
    ho_bbl = ho * 42.0
    margin = ((2.0 * gas_bbl + ho_bbl) - (3.0 * cl)) / 3.0
    signal = margin >= 25.0 ? "SELL_CRACK" : (margin <= 10.0 ? "BUY_CRACK" : "HOLD")
    return (margin = margin, signal = signal)
end

function compute_soybean_crush(beans::Float64, meal::Float64, oil::Float64)
    meal_rev = meal * 2.2
    oil_rev = oil * 11.0
    gpm = (meal_rev + oil_rev) - beans
    signal = gpm > 180.0 ? "REVERSE_CRUSH" : (gpm < 60.0 ? "CRUSH" : "HOLD")
    return (gpm = gpm, signal = signal)
end

end
