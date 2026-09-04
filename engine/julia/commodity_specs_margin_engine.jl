# Module AS5 (Julia): Futures Contract Specifications, Tick Multipliers & SPAN Margin Engine
# Quantitative evaluation of SPAN initial/maintenance margin, leverage ratios, and liquidation buffers.

module CommoditySpecsMarginEngine

export audit_margin

function audit_margin(equity::Float64, initial_m::Float64, maint_m::Float64)
    excess = equity - maint_m
    util = (initial_m / max(1.0, equity)) * 100.0
    prox = initial_m > maint_m ? ((equity - maint_m) / (initial_m - maint_m)) : 1.0
    is_safe = prox >= 1.0

    return (
        excess = excess,
        utilization = util,
        proximity = prox,
        is_safe = is_safe
    )
end

end
