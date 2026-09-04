# Module BE5 (Julia): Karl Domm All-Weather Options Portfolio & Tail Risk Vomma Engine
# Quantitative evaluation of SPAN margin slicing, 4 market regimes, and 5-delta teenie put positive vomma in Julia.

module AllWeatherVommaEngine

export classify_regime, audit_margin, evaluate_teenies

function classify_regime(spx_return::Float64, vix_spike::Float64)
    if vix_spike >= 35.0
        return "CRASH_MARKET"
    elseif spx_return < -8.0 && vix_spike < 30.0
        return "GRIND_DOWN_MARKET"
    elseif abs(spx_return) <= 4.0
        return "SIDEWAYS_MARKET"
    else
        return "RISING_BULL_MARKET"
    end
end

function audit_margin(pnl_12_down::Float64, pnl_20_down::Float64, pnl_10_up::Float64, capital::Float64)
    s12 = abs(min(0.0, pnl_12_down))
    s20 = abs(min(0.0, pnl_20_down)) / 2.0
    s10 = abs(min(0.0, pnl_10_up))

    req = max(s12, max(s20, s10))
    util = (req / max(1.0, capital)) * 100.0
    safe = util <= 65.0

    return (req = req, util = util, is_safe = safe)
end

function evaluate_teenies(core_vomma::Float64, num_teenies::Int)
    net_vomma = core_vomma + (num_teenies * 0.08)
    pos_vomma = net_vomma > 0.0
    return (net_vomma = net_vomma, has_positive_vomma = pos_vomma)
end

end
