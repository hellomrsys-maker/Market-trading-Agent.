module RatioBackspreadEngineModule

export RatioBackspreadState, construct_backspread, calculate_pnl

struct RatioBackspreadState
    short_strike::Float64
    long_strike::Float64
    net_debit_credit::Float64
    max_loss_point::Float64
    upper_bep::Float64
    lower_bep::Float64
    is_call::Bool
end

function construct_backspread(atm::Float64, otm::Float64, short_prem::Float64, long_prem::Float64, is_call::Bool)::RatioBackspreadState
    net_flow = (2.0 * long_prem) - short_prem
    max_loss = abs(otm - atm) + net_flow
    upper_bep = otm + max_loss
    lower_bep = atm + (net_flow < 0.0 ? net_flow : 0.0)
    return RatioBackspreadState(atm, otm, net_flow, max_loss, upper_bep, lower_bep, is_call)
end

function calculate_pnl(state::RatioBackspreadState, st::Float64)::Float64
    if state.is_call
        short_val = max(0.0, st - state.short_strike)
        long_val = 2.0 * max(0.0, st - state.long_strike)
        return (long_val - short_val) - state.net_debit_credit
    else
        short_val = max(0.0, state.short_strike - st)
        long_val = 2.0 * max(0.0, state.long_strike - st)
        return (long_val - short_val) - state.net_debit_credit
    end
end

end
