module KaChingConvexityEngineModule

export KaChingConvexityState, initialize_kaching, evaluate_harvest

struct KaChingConvexityState
    long_put_strike::Float64
    short_put_strike::Float64
    long_put_delta::Float64
    short_put_delta::Float64
    net_weekly_premium::Float64
    cumulative_cash::Float64
    days_to_earnings::Int32
    roll_count::Int16
    double_dip_active::Bool
end

function initialize_kaching(spot::Float64, iv::Float64, dte::Int32)::KaChingConvexityState
    long_delta = iv > 0.35 ? 0.38 : 0.25
    long_strike = spot * (1.0 - (long_delta == 0.25 ? 0.08 : 0.05))
    short_delta = spot >= long_strike ? 0.50 : 0.40
    prem = spot * 0.018 * (1.0 + iv)
    return KaChingConvexityState(long_strike, spot, long_delta, short_delta, prem, prem, dte, 0, false)
end

function evaluate_harvest(state::KaChingConvexityState, cur_prem::Float64, day_of_week::Int)::Tuple{String, Float64}
    banked_pct = 1.0 - (cur_prem / max(0.01, state.net_weekly_premium))
    if banked_pct >= 0.80 && day_of_week <= 3
        return ("DOUBLE_DIP", state.cumulative_cash + (state.net_weekly_premium * 0.60))
    elseif cur_prem > 2.0 * state.net_weekly_premium && day_of_week >= 3
        return ("ROLL_DOWN", state.cumulative_cash + ((state.net_weekly_premium * 1.15) - cur_prem))
    else
        return ("HOLD", state.cumulative_cash)
    end
end

end
