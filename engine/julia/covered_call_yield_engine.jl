# Module AP5 (Julia): Dynamic Covered Call Yield & Dividend Capture Optimizer Engine
# Quantitative attribution of static/max covered call yield and early ex-dividend assignment risk.

module CoveredCallYieldEngine

export evaluate_covered_call

function evaluate_covered_call(basis::Float64, spot::Float64, strike::Float64, premium::Float64, dte::Float64, dividend::Float64)
    be = basis - premium
    static_y = ((premium + dividend) / basis) * 100.0
    ann_static = static_y * (365.0 / max(1.0, dte))

    cap_gain = max(0.0, strike - basis)
    max_y = ((cap_gain + premium + dividend) / basis) * 100.0
    ann_max = max_y * (365.0 / max(1.0, dte))

    intrinsic = max(0.0, spot - strike)
    extrinsic = max(0.0, premium - intrinsic)
    early_assignment = (spot > strike) && (extrinsic < dividend)

    return (
        breakeven = be,
        annualized_static = ann_static,
        annualized_max = ann_max,
        early_assignment = early_assignment
    )
end

end
